import unittest

from ..common import ApiTestBase, compat_mock


class UsertagsTests(ApiTestBase):
    """Tests for UsertagsEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_usertag_feed',
                'test': UsertagsTests('test_usertag_feed', api, user_id='329452045')
            },
            {
                'name': 'test_usertag_self_remove',
                'test': UsertagsTests('test_usertag_self_remove', api, media_id='???')
            },
            {
                'name': 'test_usertag_self_remove_mock',
                'test': UsertagsTests('test_usertag_self_remove_mock', api, media_id='???')
            },
        ]

    def test_usertag_feed(self):
        results = self.api.usertag_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    @unittest.skip('Modifies data. Needs info setup.')
    def test_usertag_self_remove(self):
        results = self.api.usertag_self_remove(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_usertag_self_remove_mock(self, call_api):
        media_id = '123'
        call_api.return_value = {
            'status': 'ok',
            'media': {
                'pk': 123, 'code': 'abc', 'taken_at': 1234567890,
                'media_type': 1, 'caption': None,
                'user': {
                    'pk': 123, 'biography': '',
                    'profile_pic_url': 'https://example.com/x.jpg',
                    'external_url': ''
                }
            }
        }
        self.api.usertag_self_remove(media_id)
        call_api.assert_called_with(
            'usertags/{media_id!s}/remove/'.format(**{'media_id': media_id}),
            params=self.api.authenticated_params)
