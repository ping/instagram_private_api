import unittest
import json
try:
    # python 2.x
    from urllib2 import urlopen
except ImportError:
    # python 3.x
    from urllib.request import urlopen

from ..common import ApiTestBase


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
