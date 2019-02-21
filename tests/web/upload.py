import unittest
import time
try:
    # python 2.x
    from urllib2 import urlopen
except ImportError:
    # python 3.x
    from urllib.request import urlopen
import json

from ..common import WebApiTestBase, MockResponse, compat_mock


class UploadTests(WebApiTestBase):
    """Tests for ClientCompatPatch."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_post_photo',
                'test': UploadTests('test_post_photo', api),
            },
            {
                'name': 'test_post_photo_mock',
                'test': UploadTests('test_post_photo_mock', api),
            },
        ]

    @unittest.skip('Modifies data')
    def test_post_photo(self):
        sample_url = 'https://c1.staticflickr.com/5/4103/5059663679_85a7ec3f63_b.jpg'
        res = urlopen(sample_url)
        photo_data = res.read()
        results = self.api.post_photo(photo_data, caption='Feathers #feathers')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_post_photo_mock(self, make_request):
        ts_now = time.time()
        make_request.return_value = {'status': 'ok', 'upload_id': '123456789'}
        with compat_mock.patch(
                'instagram_web_api.client.compat_urllib_request.OpenerDirector.open') as opener, \
                compat_mock.patch('instagram_web_api.client.time.time') as time_mock, \
                compat_mock.patch('instagram_web_api.client.random.choice') as rand_choice, \
                compat_mock.patch('instagram_web_api.Client._read_response') as read_response, \
                compat_mock.patch(
                    'instagram_web_api.client.compat_urllib_request.Request') as request:
            opener.return_value = MockResponse()
            time_mock.return_value = ts_now
            rand_choice.return_value = 'x'
            # add rhx_gis so that we can reuse the same response for init and uploading
            read_response.return_value = json.dumps(
                {'status': 'ok', 'upload_id': '123456789', 'rhx_gis': '22aea71b163e335a0ad4479549b530d7'},
                separators=(',', ':')
            )
            self.api.post_photo('...'.encode('ascii'), caption='Test')

            headers = {
                'Accept-Language': 'en-US',
                'Accept-Encoding': 'gzip, deflate',
                'Origin': 'https://www.instagram.com',
                'x-csrftoken': self.api.csrftoken,
                'x-instagram-ajax': '1',
                'Accept': '*/*',
                'User-Agent': self.api.mobile_user_agent,
                'Referer': 'https://www.instagram.com/create/details/',
                'x-requested-with': 'XMLHttpRequest',
                'Connection': 'close',
                'Content-Type': 'application/x-www-form-urlencoded'}

            body = '--{boundary}\r\n' \
                   'Content-Disposition: form-data; name="upload_id"\r\n\r\n' \
                   '{upload_id}\r\n' \
                   '--{boundary}\r\n' \
                   'Content-Disposition: form-data; name="media_type"\r\n\r\n1\r\n' \
                   '--{boundary}\r\n' \
                   'Content-Disposition: form-data; name="photo"; filename="photo.jpg"\r\n' \
                   'Content-Type: application/octet-stream\r\n' \
                   'Content-Transfer-Encoding: binary\r\n\r\n...\r\n' \
                   '--{boundary}--\r\n'.format(
                       boundary='----WebKitFormBoundary{}'.format('x' * 16),
                       upload_id=int(ts_now * 1000))
            request.assert_called_with(
                'https://www.instagram.com/create/upload/photo/',
                body.encode('utf-8'), headers=headers)
