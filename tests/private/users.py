import unittest

from ..common import (
    ApiTestBase, compat_mock, ClientError
)


class UsersTests(ApiTestBase):
    """Tests for UsersEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_user_info',
                'test': UsersTests('test_user_info', api, user_id='124317')
            },
            {
                # private user
                'name': 'test_user_info2',
                'test': UsersTests('test_user_info', api, user_id='426095486')
            },
            {
                'name': 'test_deleted_user_info',
                'test': UsersTests('test_deleted_user_info', api, user_id='322244991')
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
            {
                'name': 'test_user_reel_settings',
                'test': UsersTests('test_user_reel_settings', api)
            },
            {
                'name': 'test_set_reel_settings_mock',
                'test': UsersTests('test_set_reel_settings_mock', api)
            },
            {
                'name': 'test_blocked_user_list',
                'test': UsersTests('test_blocked_user_list', api)
            },
        ]

    def test_user_info(self):
        results = self.api.user_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user', {}).get('profile_picture'))

    def test_deleted_user_info(self):
        with self.assertRaises(ClientError) as ce:
            self.api.user_info(self.test_user_id)
        self.assertEqual(ce.exception.code, 404)

    def test_username_info(self):
        results = self.api.username_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user', {}).get('profile_picture'))

    def test_user_detail_info(self):
        results = self.api.user_detail_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('feed', {}).get('items', [])), 0, 'No items returned.')

    @unittest.skip('Deprecated.')
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

    def test_blocked_user_list(self):
        results = self.api.blocked_user_list()
        self.assertEqual(results.get('status'), 'ok')
        self.assertTrue('blocked_list' in results)

    def test_user_reel_settings(self):
        results = self.api.user_reel_settings()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('message_prefs'))
        self.assertTrue('blocked_reels' in results)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_set_reel_settings_mock(self, call_api):
        call_api.return_value = {'status': 'ok', 'message_prefs': 'anyone'}
        params = {'message_prefs': call_api.return_value['message_prefs']}
        params.update(self.api.authenticated_params)
        self.api.set_reel_settings(call_api.return_value['message_prefs'])
        call_api.assert_called_with('users/set_reel_settings/', params=params)

        with self.assertRaises(ValueError) as ve:
            self.api.set_reel_settings('x')
        self.assertEqual(str(ve.exception), 'Invalid message_prefs: x')
