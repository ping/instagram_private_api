import unittest
import json
import time
from io import BytesIO
try:
    # python 2.x
    from urllib2 import urlopen
except ImportError:
    # python 3.x
    from urllib.request import urlopen

from ..common import ClientError, ApiTestBase, compat_mock, compat_urllib_error, MockResponse


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
            {
                'name': 'test_post_video_mock',
                'test': UploadTests('test_post_video_mock', api)
            },
            {
                'name': 'test_post_album_mock',
                'test': UploadTests('test_post_album_mock', api)
            },
            {
                'name': 'test_post_album_validation_mock',
                'test': UploadTests('test_post_album_validation_mock', api)
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

    def test_post_photo_base(self, size=(800, 800), caption='HEY', upload_id=None, location=None,
                             disable_comments=False, is_reel=False, is_sidecar=False, **kwargs):
        ts_now = time.time()
        with compat_mock.patch(
                'instagram_private_api.endpoints.accounts.compat_urllib_request.OpenerDirector.open') as opener, \
                compat_mock.patch('instagram_private_api.Client._read_response') as read_response, \
                compat_mock.patch('instagram_private_api.Client.default_headers') as default_headers, \
                compat_mock.patch(
                    'instagram_private_api.endpoints.accounts.compat_urllib_request.Request') as request, \
                compat_mock.patch('instagram_private_api.Client._call_api') as call_api, \
                compat_mock.patch('instagram_private_api.endpoints.upload.time.time') as time_mock, \
                compat_mock.patch('instagram_private_api.endpoints.upload.randint') as randint_mock:
            time_mock.return_value = ts_now
            randint_mock.return_value = 0
            # for photo posting
            default_headers.return_value = {'Header': 'X'}

            if kwargs.pop('raise_httperror', False):
                opener.side_effect = [compat_urllib_error.HTTPError(
                    'http://localhost', 400, 'Bad Request', {},
                    BytesIO(json.dumps({'status': 'fail', 'message': 'Invalid Request'}).encode('ascii')))]
            else:
                opener.side_effect = [MockResponse()]

            if upload_id:
                for_video = True
            else:
                for_video = False
                upload_id = str(int(ts_now * 1000))
            read_response.return_value = json.dumps({'status': 'ok', 'upload_id': upload_id})
            # for configure
            call_api.return_value = {
                'status': 'ok',
                'media': {
                    'code': 'x', 'taken_at': 149000000, 'media_type': 1, 'caption': None,
                    'user': {'pk': 10, 'profile_pic_url': ''}}
            }

            photo_data = '...'.encode('ascii')
            headers = self.api.default_headers
            headers.update({
                'Content-Type': 'multipart/form-data; boundary=%s' % self.api.uuid,
                'Content-Length': len(photo_data)
            })
            sidecar_fields = ''
            if is_sidecar:
                sidecar_fields = 'Content-Disposition: form-data; name="is_sidecar"\r\n\r\n' \
                                 '1\r\n' \
                                 '--%(uuid)s\r\n' % {'uuid': self.api.uuid}

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
                   '%(sidecar_fields)s' \
                   'Content-Disposition: form-data; name="photo"; filename="pending_media_%(ts)s.jpg"\r\n' \
                   'Content-Type: application/octet-stream\r\n' \
                   'Content-Transfer-Encoding: binary\r\n\r\n...\r\n' \
                   '--%(uuid)s--\r\n'\
                   % {'uuid': self.api.uuid,
                      'csrftoken': self.api.csrftoken,
                      'upload_id': upload_id,
                      'ts': str(int(ts_now * 1000)),
                      'sidecar_fields': sidecar_fields}

            if not is_reel:
                if for_video:
                    self.api.post_photo(
                        photo_data, size, caption=caption, upload_id=upload_id,
                        location=location, disable_comments=disable_comments,
                        is_sidecar=is_sidecar)
                else:
                    self.api.post_photo(
                        photo_data, size, caption=caption,
                        location=location, disable_comments=disable_comments,
                        is_sidecar=is_sidecar)
            else:
                self.api.post_photo_story(photo_data, size)

            request.assert_called_with(
                self.api.api_url + 'upload/photo/',
                body.encode('utf-8'), headers=headers)

            if not is_reel:
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
                if location:
                    media_loc = self.api._validate_location(location)
                    configure_params['location'] = json.dumps(media_loc)
                    configure_params['geotag_enabled'] = '1'
                    configure_params['exif_latitude'] = '0.0'
                    configure_params['exif_longitude'] = '0.0'
                    configure_params['posting_latitude'] = str(location['lat'])
                    configure_params['posting_longitude'] = str(location['lng'])
                    configure_params['media_latitude'] = str(location['lat'])
                    configure_params['media_latitude'] = str(location['lng'])
                if disable_comments:
                    configure_params['disable_comments'] = '1'

                configure_params.update(self.api.authenticated_params)
                if not is_sidecar:
                    call_api.assert_called_with(
                        'media/configure/', params=configure_params
                    )
            else:
                configure_params = {
                    'source_type': '4',
                    'upload_id': upload_id,
                    'story_media_creation_date': str(int(ts_now)),
                    'client_shared_at': str(int(ts_now)),
                    'client_timestamp': str(int(ts_now)),
                    'configure_mode': 1,      # 1 - REEL_SHARE, 2 - DIRECT_STORY_SHARE
                    'device': {
                        'manufacturer': self.api.phone_manufacturer,
                        'model': self.api.phone_device,
                        'android_version': self.api.android_version,
                        'android_release': self.api.android_release
                    },
                    'edits': {
                        'crop_original_size': [size[0] * 1.0, size[1] * 1.0],
                        'crop_center': [0.0, 0.0],
                        'crop_zoom': 1.3333334
                    },
                    'extra': {
                        'source_width': size[0],
                        'source_height': size[1],
                    }
                }
                configure_params.update(self.api.authenticated_params)
                call_api.assert_called_with(
                    'media/configure_to_story/', params=configure_params
                )

    def test_post_photo_mock(self):

        location_results = self.api.location_search('40.7484445', '-73.9878531', query='Empire')
        location = location_results.get('venues', [{}])[0] or None

        self.test_post_photo_base(location=location, disable_comments=True)

        with self.assertRaises(ValueError) as ve:
            self.test_post_photo_base(size=(3000, 3000))
        self.assertEqual(str(ve.exception), 'Invalid image width.')

        with self.assertRaises(ValueError) as ve:
            self.test_post_photo_base(size=(1080, 300))
        self.assertEqual(str(ve.exception), 'Incompatible aspect ratio.')

        with self.assertRaises(ValueError) as ve:
            self.test_post_photo_base(location='X')
        self.assertEqual(str(ve.exception), 'Location must be a dict.')

        with self.assertRaises(ValueError) as ve:
            location.pop('address', None)
            self.test_post_photo_base(location=location)
        self.assertEqual(str(ve.exception), 'Location dict must contain "address".')

        with self.assertRaises(ClientError) as ce:
            self.test_post_photo_base(raise_httperror=True)
        self.assertEqual(ce.exception.msg, 'Bad Request')

        # Stories
        self.test_post_photo_base(size=(608, 1080), is_reel=True)
        with self.assertRaises(ValueError) as ve:
            self.test_post_photo_base(size=(1080, 1080), is_reel=True)
        self.assertEqual(str(ve.exception), 'Incompatible reel aspect ratio.')

        # Test album
        self.test_post_photo_base(is_sidecar=True)

    def test_post_video_base(self, size, duration, caption='', location=None,
                             disable_comments=False, to_reel=False, is_sidecar=False,
                             **kwargs):
        ts_now = time.time()
        with compat_mock.patch('instagram_private_api.Client._call_api') as call_api, \
                compat_mock.patch(
                    'instagram_private_api.endpoints.accounts.compat_urllib_request.OpenerDirector.open') as opener, \
                compat_mock.patch('instagram_private_api.Client._read_response') as read_response, \
                compat_mock.patch('instagram_private_api.Client.default_headers') as default_headers, \
                compat_mock.patch(
                    'instagram_private_api.endpoints.accounts.compat_urllib_request.Request') as request, \
                compat_mock.patch('instagram_private_api.endpoints.upload.time.time') as time_mock, \
                compat_mock.patch('instagram_private_api.endpoints.upload.randint') as randint_mock:

            time_mock.return_value = ts_now
            randint_mock.return_value = 0
            default_headers.return_value = {'Header': 'X'}
            video_data = ('.' * 16).encode('ascii')
            thumbnail_data = '....'.encode('ascii')
            upload_id = str(int(ts_now * 1000))

            raise_httperror = kwargs.pop('raise_httperror', False)
            opener.side_effect = [
                MockResponse(),     # chunk 1
                MockResponse(),     # chunk 2
                MockResponse() if not raise_httperror else compat_urllib_error.HTTPError(
                    'http://localhost', 400, 'Bad Request', {},
                    BytesIO(json.dumps({'status': 'fail', 'message': 'Invalid Request'}).encode('ascii'))),  # chunk 3
                MockResponse(content_type='application/json'),
                MockResponse(),     # For uploading thmbnail
            ]

            call_api.side_effect = [
                {'video_upload_urls': [{'url': 'http://localhost', 'job': '1111'}]},  # Upload request
                {'status': 'ok'},    # Upload photo thumbnail request
                {'status': 'ok', 'media':
                    {'code': 'x', 'taken_at': 149000000, 'media_type': 1, 'caption': None,
                     'user': {'pk': 10, 'profile_pic_url': ''}}},    # Configure video request
            ]
            read_response.side_effect = [
                '0-3/16',           # 1st response to chunk upload
                '4-7/16',           # 2nd response to chunk upload
                '8-11/16',          # 3rd response to chunk upload
                json.dumps({'status': 'ok'}),  # Last response to chunk
                json.dumps({'status': 'ok', 'upload_id': upload_id}),   # Response to thumbnail upload
            ]

            upload_params = {
                '_csrftoken': self.api.csrftoken,
                '_uuid': self.api.uuid,
                'upload_id': upload_id,
            }
            if is_sidecar:
                upload_params['is_sidecar'] = '1'
            else:
                upload_params.update({
                    'media_type': '2',
                    'upload_media_duration_ms': int(duration * 1000),
                    'upload_media_width': size[0],
                    'upload_media_height': size[1]
                })

            if not to_reel:
                self.api.post_video(
                    video_data, size=size, duration=duration,
                    thumbnail_data=thumbnail_data, caption=caption,
                    location=location, disable_comments=disable_comments,
                    is_sidecar=is_sidecar)
            else:
                self.api.post_video_story(
                    video_data, size=size, duration=duration,
                    thumbnail_data=thumbnail_data
                )

            call_api.assert_any_call('upload/video/', params=upload_params, unsigned=True)

            headers = self.api.default_headers
            headers['Connection'] = 'keep-alive'
            headers['Content-Type'] = 'application/octet-stream'
            headers['Content-Disposition'] = 'attachment; filename="video.mov"'
            headers['Session-ID'] = upload_id
            if is_sidecar:
                headers['Cookie'] = 'sessionid=' + self.api.get_cookie_value('sessionid')
            headers['job'] = '1111'
            headers['Content-Length'] = 4
            headers['Content-Range'] = 'bytes %d-%d/%d' % (0, 3, 4)
            request.assert_any_call(
                'http://localhost', data=video_data[0:4], headers=headers)

            if not to_reel:
                configure_params = {
                    'upload_id': upload_id,
                    'caption': caption,
                    'source_type': '3',
                    'poster_frame_index': 0,
                    'length': duration * 1.0,
                    'audio_muted': False,
                    'filter_type': '0',
                    'video_result': 'deprecated',
                    'clips': {
                        'length': duration * 1.0,
                        'source_type': '3',
                        'camera_position': 'back'
                    },
                    'device': {
                        'manufacturer': self.api.phone_manufacturer,
                        'model': self.api.phone_device,
                        'android_version': self.api.android_version,
                        'android_release': self.api.android_release
                    },
                    'extra': {
                        'source_width': size[0],
                        'source_height': size[1],
                    }
                }
                if location:
                    media_loc = self.api._validate_location(location)
                    configure_params['location'] = json.dumps(media_loc)
                    configure_params['geotag_enabled'] = '1'
                    configure_params['av_latitude'] = '0.0'
                    configure_params['av_longitude'] = '0.0'
                    configure_params['posting_latitude'] = str(location['lat'])
                    configure_params['posting_longitude'] = str(location['lng'])
                    configure_params['media_latitude'] = str(location['lat'])
                    configure_params['media_latitude'] = str(location['lng'])
                if disable_comments:
                    configure_params['disable_comments'] = '1'

                configure_params.update(self.api.authenticated_params)
                if not is_sidecar:
                    call_api.assert_called_with('media/configure/', params=configure_params, query={'video': 1})
            else:
                configure_params = {
                    'source_type': '4',
                    'upload_id': upload_id,
                    'story_media_creation_date': str(int(ts_now)),
                    'client_shared_at': str(int(ts_now)),
                    'client_timestamp': str(int(ts_now)),
                    'configure_mode': 1,      # 1 - REEL_SHARE, 2 - DIRECT_STORY_SHARE
                    'poster_frame_index': 0,
                    'length': duration * 1.0,
                    'audio_muted': False,
                    'filter_type': '0',
                    'video_result': 'deprecated',
                    'clips': {
                        'length': duration * 1.0,
                        'source_type': '4',
                        'camera_position': 'back'
                    },
                    'device': {
                        'manufacturer': self.api.phone_manufacturer,
                        'model': self.api.phone_device,
                        'android_version': self.api.android_version,
                        'android_release': self.api.android_release
                    },
                    'extra': {
                        'source_width': size[0],
                        'source_height': size[1],
                    },
                }
                configure_params.update(self.api.authenticated_params)
                call_api.assert_called_with('media/configure_to_story/', params=configure_params, query={'video': '1'})

    def test_post_video_mock(self):
        location_results = self.api.location_search('40.7484445', '-73.9878531', query='Empire')
        location = location_results.get('venues', [{}])[0] or None

        self.test_post_video_base(
            (800, 800), 15, caption='HEY', location=location, disable_comments=True)

        with self.assertRaises(ValueError) as ve:
            self.test_post_video_base((600, 600), 15, 'HEY')
        self.assertEqual(str(ve.exception), 'Invalid video width.')

        with self.assertRaises(ValueError) as ve:
            self.test_post_video_base((800, 800), 2, 'HEY')
        self.assertEqual(str(ve.exception), 'Duration is less than 3s.')

        with self.assertRaises(ValueError) as ve:
            self.test_post_video_base((800, 800), 61, 'HEY')
        self.assertEqual(str(ve.exception), 'Duration is more than 60s.')

        # Stories
        self.test_post_video_base(size=(612, 1080), duration=15, to_reel=True)

        with self.assertRaises(ValueError) as ve:
            self.test_post_video_base(size=(612, 1080), duration=16, to_reel=True)
        self.assertEqual(str(ve.exception), 'Duration is more than 15s.')

        with self.assertRaises(ClientError) as ce:
            self.test_post_video_base(size=(800, 800), duration=16, raise_httperror=True)
        self.assertEqual(ce.exception.msg, 'Bad Request')

        # Album
        self.test_post_video_base(
            (800, 800), 15, caption='HEY', is_sidecar=True)

    def test_post_album_mock(self):
        ts_now = time.time()
        with compat_mock.patch('instagram_private_api.Client._call_api') as call_api, \
                compat_mock.patch('instagram_private_api.Client.post_photo') as post_photo, \
                compat_mock.patch('instagram_private_api.Client.post_video') as post_video, \
                compat_mock.patch('instagram_private_api.endpoints.upload.time.time') as time_mock:

            time_mock.return_value = ts_now
            post_photo.side_effect = [{'status': 'ok'}, {'status': 'ok'}]
            post_video.side_effect = [{'status': 'ok'}]
            call_api.return_value = {'status': 'ok'}

            location = {
                'name': 'Empire State Building',
                'external_id_source': 'facebook_places',
                'address': "New York",
                'lat': 40.749003253823,
                'lng': -73.985594775582,
                'external_id': '153817204635459'
            }

            album_upload_id = str(int(ts_now * 1000))
            disable_comments = True
            caption = 'HEY'
            medias = [
                {'type': 'image', 'size': (800, 800), 'data': '...'},
                {
                    'type': 'image', 'size': (720, 720),
                    'usertags': [{'user_id': 4292127751, 'position': [0.625347, 0.4384531]}],
                    'data': "..."
                },
                {'type': 'video', 'size': (720, 720), 'duration': 12.4, 'thumbnail': '...', 'data': '...'}
            ]
            self.api.post_album(medias, caption=caption, location=location, disable_comments=disable_comments)

            children_metadata = []
            for media in medias:
                metadata = {'status': 'ok'}
                if media.get('usertags'):
                    usertags = media['usertags']
                    utags = {'in': [{'user_id': str(u['user_id']), 'position': u['position']} for u in usertags]}
                    metadata['usertags'] = json.dumps(utags, separators=(',', ':'))
                children_metadata.append(metadata)
            params = {
                'caption': caption,
                'client_sidecar_id': album_upload_id,
                'children_metadata': children_metadata
            }
            if location:
                media_loc = self.api._validate_location(location)
                params['location'] = json.dumps(media_loc)
                if 'lat' in location and 'lng' in location:
                    params['geotag_enabled'] = '1'
                    params['exif_latitude'] = '0.0'
                    params['exif_longitude'] = '0.0'
                    params['posting_latitude'] = str(location['lat'])
                    params['posting_longitude'] = str(location['lng'])
                    params['media_latitude'] = str(location['lat'])
                    params['media_latitude'] = str(location['lng'])
            if disable_comments:
                params['disable_comments'] = '1'
            params.update(self.api.authenticated_params)
            call_api.assert_called_with('media/configure_sidecar/', params=params)

    def test_post_album_validation_mock(self):
        disable_comments = True
        caption = 'HEY'
        medias = [
            {'type': 'imagex', 'size': (800, 800), 'data': '...'},
            {'type': 'image', 'size': (800, 800), 'data': '...'},
        ]
        with self.assertRaises(ValueError) as ve:
            self.api.post_album(medias, caption=caption, disable_comments=disable_comments)
        self.assertEqual(str(ve.exception), 'Invalid media type: imagex')

        medias = [
            {'type': 'image', 'size': (800, 800)},
            {'type': 'image', 'data': '...'},
        ]
        with self.assertRaises(ValueError) as ve:
            self.api.post_album(medias, caption=caption, disable_comments=disable_comments)
        self.assertEqual(str(ve.exception), 'Data not specified.')

        medias = [
            {'type': 'image', 'data': '...'},
            {'type': 'image', 'size': (800, 800), 'data': '...'},
        ]
        with self.assertRaises(ValueError) as ve:
            self.api.post_album(medias, caption=caption, disable_comments=disable_comments)
        self.assertEqual(str(ve.exception), 'Size not specified.')

        medias = [
            {'type': 'video', 'size': (720, 720), 'thumbnail': '...', 'data': '...'},
            {'type': 'image', 'size': (800, 800), 'data': '...'},
        ]
        with self.assertRaises(ValueError) as ve:
            self.api.post_album(medias, caption=caption, disable_comments=disable_comments)
        self.assertEqual(str(ve.exception), 'Duration not specified.')

        medias = [
            {'type': 'video', 'size': (720, 720), 'duration': 12.4, 'data': '...'},
            {'type': 'image', 'size': (800, 800), 'data': '...'},
        ]
        with self.assertRaises(ValueError) as ve:
            self.api.post_album(medias, caption=caption, disable_comments=disable_comments)
        self.assertEqual(str(ve.exception), 'Thumbnail not specified.')

        medias = [
            {'type': 'image', 'size': (800, 600), 'data': '...'},
            {'type': 'image', 'size': (800, 800), 'data': '...'},
        ]
        with self.assertRaises(ValueError) as ve:
            self.api.post_album(medias, caption=caption, disable_comments=disable_comments)
        self.assertEqual(str(ve.exception), 'Invalid media aspect ratio.')
