import unittest
import json
import time
try:
    # python 2.x
    from urllib2 import urlopen
except ImportError:
    # python 3.x
    from urllib.request import urlopen

from ..common import ApiTestBase, compat_mock


class UploadTests(ApiTestBase):

    @classmethod
    def init_all(cls, api):
        return [
            {
                'name': 'test_post_photo',
                'test': UploadTests('test_post_photo', api)
            },
            {
                'name': 'test_post_video',
                'test': UploadTests('test_post_video', api)
            },
            {
                'name': 'test_post_album',
                'test': UploadTests('test_post_album', api)
            },
            {
                'name': 'test_post_photo_story',
                'test': UploadTests('test_post_photo_story', api)
            },
            {
                'name': 'test_post_video_story',
                'test': UploadTests('test_post_video_story', api)
            },
            {
                'name': 'test_post_photo_mock',
                'test': UploadTests('test_post_photo_mock', api)
            },
        ]

    @unittest.skip('Modifies data.')
    def test_post_photo(self):
        sample_url = 'https://c1.staticflickr.com/5/4103/5059663679_85a7ec3f63_b.jpg'
        res = urlopen(sample_url)
        photo_data = res.read()
        size = (1024, 683)
        results = self.api.post_photo(photo_data, size=size, caption='')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_video(self):
        # Reposting from https://www.instagram.com/p/BL5hkEHDyd5/
        media_id = '1367271575733086073_2958144170'
        res = self.api.media_info(media_id)
        media_info = res['items'][0]
        video_url = media_info['videos']['standard_resolution']['url']
        video_size = (media_info['videos']['standard_resolution']['width'],
                      media_info['videos']['standard_resolution']['height'])
        thumbnail_url = media_info['images']['standard_resolution']['url']
        video_res = urlopen(video_url)
        video_data = video_res.read()
        thumb_res = urlopen(thumbnail_url)
        thumb_data = thumb_res.read()
        duration = media_info['video_duration']
        results = self.api.post_video(video_data, video_size, duration, thumb_data, caption='<3')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_photo_story(self):
        sample_url = 'http://i.imgur.com/3QzazV2.jpg'
        res = urlopen(sample_url)
        photo_data = res.read()
        size = (1080, 1920)
        results = self.api.post_photo_story(photo_data, size)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_video_story(self):
        # Reposting https://streamable.com/08ico
        video_info_res = urlopen('https://api.streamable.com/videos/08ico')
        video_info = json.loads(video_info_res.read().decode('utf8'))
        mp4_info = video_info['files']['mp4']

        video_url = ('https:' if mp4_info['url'].startswith('//') else '') + mp4_info['url']
        video_size = (mp4_info['width'], mp4_info['height'])
        thumbnail_url = ('https:' if video_info['thumbnail_url'].startswith('//') else '') + video_info['thumbnail_url']
        duration = mp4_info['duration']

        video_res = urlopen(video_url)
        video_data = video_res.read()
        thumb_res = urlopen(thumbnail_url)
        thumb_data = thumb_res.read()
        results = self.api.post_video_story(video_data, video_size, duration, thumb_data)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_album(self):
        # Reposting from https://www.instagram.com/p/BL5hkEHDyd5/
        media_id = '1367271575733086073_2958144170'
        res = self.api.media_info(media_id)
        media_info = res['items'][0]
        video_url = media_info['videos']['standard_resolution']['url']
        video_size = (media_info['videos']['standard_resolution']['width'],
                      media_info['videos']['standard_resolution']['height'])
        thumbnail_url = media_info['images']['standard_resolution']['url']
        video_res = urlopen(video_url)
        video_data = video_res.read()
        thumb_res = urlopen(thumbnail_url)
        thumb_data = thumb_res.read()
        duration = media_info['video_duration']
        medias = [
            {
                'type': 'image', 'size': video_size, 'data': thumb_data
            },
            {
                'type': 'video', 'size': video_size, 'duration': duration,
                'thumbnail': thumb_data, 'data': video_data
            }
        ]
        results = self.api.post_album(medias, caption='Testing...')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @compat_mock.patch('instagram_private_api.endpoints.accounts.compat_urllib_request.OpenerDirector.open')
    def test_post_photo_mock(self, opener):

        ts_now = time.time()
        with compat_mock.patch('instagram_private_api.Client._read_response') as read_response, \
                compat_mock.patch('instagram_private_api.Client.default_headers') as default_headers, \
                compat_mock.patch(
                    'instagram_private_api.endpoints.accounts.compat_urllib_request.Request') as request, \
                compat_mock.patch('instagram_private_api.Client._call_api') as call_api, \
                compat_mock.patch('instagram_private_api.endpoints.upload.time.time') as time_mock:

            time_mock.return_value = ts_now
            # for photo posting
            default_headers.return_value = {'Header': 'X'}

            class MockResponse(object):
                def __init__(self):
                    self.code = 200
            opener.return_value = MockResponse()

            upload_id = str(int(ts_now * 1000))
            read_response.return_value = json.dumps({'status': 'ok', 'upload_id': upload_id})
            # for configure
            call_api.return_value = {'status': 'ok'}

            photo_data = '...'
            size = (800, 800)
            headers = self.api.default_headers
            headers.update({
                'Content-Type': 'multipart/form-data; boundary=%s' % self.api.uuid,
                'Content-Length': len(photo_data)
            })
            body = '--%(uuid)s\r\n' \
                   'Content-Disposition: form-data; name="upload_id"\r\n\r\n' \
                   '%(upload_id)s\r\n' \
                   '--%(uuid)s\r\n' \
                   'Content-Disposition: form-data; name="_uuid"\r\n\r\n' \
                   '%(uuid)s\r\n' \
                   '--%(uuid)s\r\n' \
                   'Content-Disposition: form-data; name="_csrftoken"\r\n\r\n' \
                   '%(csrftoken)s\r\n' \
                   '--%(uuid)s\r\n' \
                   'Content-Disposition: form-data; name="image_compression"\r\n\r\n' \
                   '{"lib_name":"jt","lib_version":"1.3.0","quality":"87"}\r\n' \
                   '--%(uuid)s\r\n' \
                   'Content-Disposition: form-data; name="photo"; filename="pending_media_%(ts)s.jpg"\r\n' \
                   'Content-Type: application/octet-stream\r\n' \
                   'Content-Transfer-Encoding: binary\r\n\r\n...\r\n' \
                   '--%(uuid)s--\r\n' % {'uuid': self.api.uuid,
                                         'csrftoken': self.api.csrftoken,
                                         'upload_id': upload_id,
                                         'ts': str(int(ts_now * 1000))}

            caption = 'HEY'
            self.api.post_photo(photo_data, size, caption=caption)
            request.assert_called_with(
                self.api.api_url + 'upload/photo/',
                body, headers=headers)

            configure_params = {
                'caption': caption,
                'media_folder': 'Instagram',
                'source_type': '4',
                'upload_id': upload_id,
                'device': {
                    'manufacturer': self.api.phone_manufacturer,
                    'model': self.api.phone_device,
                    'android_version': self.api.android_version,
                    'android_release': self.api.android_release
                },
                'edits': {
                    'crop_original_size': [size[0] * 1.0, size[1] * 1.0],
                    'crop_center': [0.0, -0.0],
                    'crop_zoom': 1.0
                },
                'extra': {
                    'source_width': size[0],
                    'source_height': size[1],
                }
            }
            configure_params.update(self.api.authenticated_params)
            call_api.assert_called_with(
                'media/configure/', params=configure_params
            )
