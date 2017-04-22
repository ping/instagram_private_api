
from ..common import ApiTestBase


class UsersTests(ApiTestBase):

    @classmethod
    def init_all(cls, api):
        return [
            {
                'name': 'test_user_info',
                'test': UsersTests('test_user_info', api, user_id='124317')
            },
            {
                'name': 'test_user_info2',
                'test': UsersTests('test_user_info', api, user_id='322244991')
            },
            {
                'name': 'test_username_info',
                'test': UsersTests('test_username_info', api, user_id='maruhanamogu')
            },
            {
                'name': 'test_user_detail_info',
                'test': UsersTests('test_user_detail_info', api, user_id='124317')
            },
            {
                'name': 'test_search_users',
                'test': UsersTests('test_search_users', api)
            },
            {
                'name': 'test_user_map',
                'test': UsersTests('test_user_map', api, user_id='2958144170')
            },
            {
                'name': 'test_check_username',
                'test': UsersTests('test_check_username', api)
            },
        ]

    def test_user_info(self):
        results = self.api.user_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user', {}).get('profile_picture'))

    def test_username_info(self):
        results = self.api.username_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user', {}).get('profile_picture'))

    def test_user_detail_info(self):
        results = self.api.user_detail_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('feed', {}).get('items', [])), 0, 'No items returned.')

    def test_user_map(self):
        results = self.api.user_map(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('geo_media'))

    def test_search_users(self):
        results = self.api.search_users('maruhanamogu')
        self.assertEqual(results.get('status'), 'ok')

    def test_check_username(self):
        results = self.api.check_username('instagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('available'))
        self.assertIsNotNone(results.get('error'))
        self.assertIsNotNone(results.get('error_type'))
