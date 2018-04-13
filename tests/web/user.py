import unittest
import time

from ..common import WebApiTestBase, WebClientError as ClientError, compat_mock


class UserTests(WebApiTestBase):
    """Tests for user related functions."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_user_info',
                'test': UserTests('test_user_info', api),
            },
            {
                'name': 'test_user_info2',
                'test': UserTests('test_user_info2', api),
            },
            {
                'name': 'test_user_feed',
                'test': UserTests('test_user_feed', api),
            },
            {
                'name': 'test_notfound_user_feed',
                'test': UserTests('test_notfound_user_feed', api)
            },
            {
                'name': 'test_user_feed_noextract',
                'test': UserTests('test_user_feed_noextract', api)
            },
            {
                'name': 'test_user_followers',
                'test': UserTests('test_user_followers', api),
                'require_auth': True,
            },
            {
                'name': 'test_user_followers_noextract',
                'test': UserTests('test_user_followers_noextract', api),
                'require_auth': True,
            },
            {
                'name': 'test_user_following',
                'test': UserTests('test_user_following', api),
                'require_auth': True,
            },
            {
                'name': 'test_friendships_create',
                'test': UserTests('test_friendships_create', api),
                'require_auth': True,
            },
            {
                'name': 'test_friendships_create_mock',
                'test': UserTests('test_friendships_create_mock', api),
            },
            {
                'name': 'test_friendships_destroy',
                'test': UserTests('test_friendships_destroy', api),
                'require_auth': True,
            },
            {
                'name': 'test_friendships_destroy_mock',
                'test': UserTests('test_friendships_destroy_mock', api),
            },
        ]

    @unittest.skip('Deprecated.')
    def test_user_info(self):
        results = self.api.user_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('profile_picture'))

    def test_user_info2(self):
        results = self.api.user_info2('instagram')
        self.assertIsNotNone(results.get('id'))

    def test_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_notfound_user_feed(self):
        self.assertRaises(ClientError, lambda: self.api.user_feed('1'))

    def test_user_feed_noextract(self, extract=True):
        results = self.api.user_feed(self.test_user_id, extract=False)
        self.assertIsInstance(results, dict)
        nodes = [edge['node'] for edge in results.get('data', {}).get('user', {}).get(
            'edge_owner_to_timeline_media', {}).get('edges', [])]
        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes), 0)
        first_code = nodes[0]['shortcode']
        end_cursor = results.get('data', {}).get('user', {}).get(
            'edge_owner_to_timeline_media', {}).get('page_info', {}).get('end_cursor')

        time.sleep(self.sleep_interval)
        results = self.api.user_feed(self.test_user_id, extract=False, end_cursor=end_cursor)
        self.assertNotEqual(first_code, results.get('data', {}).get('user', {}).get(
            'edge_owner_to_timeline_media', {}).get('edges', [])[0]['node']['shortcode'])

    def test_user_followers(self):
        results = self.api.user_followers(self.test_user_id)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_user_followers_noextract(self):
        results = self.api.user_followers(self.test_user_id, extract=False)
        self.assertIsInstance(results, dict)

        nodes = results.get('data', {}).get('user', {}).get(
            'edge_followed_by', {}).get('edges')
        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes or []), 0)
        first_user = nodes[0]['node']['username']
        end_cursor = results.get('data', {}).get('user', {}).get(
            'edge_followed_by', {}).get('page_info', {}).get('end_cursor')

        time.sleep(self.sleep_interval)
        results = self.api.user_followers(self.test_user_id, extract=False, end_cursor=end_cursor)
        self.assertNotEqual(first_user, results.get('data', {}).get('user', {}).get(
            'edge_followed_by', {}).get('edges')[0]['node']['username'])

    def test_user_following(self):
        results = self.api.user_following(self.test_user_id)
        self.assertGreater(len(results), 0)
        first_user = results[0]['username']

        time.sleep(self.sleep_interval)
        results = self.api.user_following(self.test_user_id, extract=False)
        end_cursor = results.get('follows', {}).get('page_info', {}).get('end_cursor')

        time.sleep(self.sleep_interval)
        results = self.api.user_following(self.test_user_id, extract=False, end_cursor=end_cursor)
        self.assertNotEqual(first_user, results.get('follows', {}).get('nodes', [{}])[0].get('username'))

    @unittest.skip('Modifies data')
    def test_friendships_create(self):
        results = self.api.friendships_create(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_friendships_create_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.friendships_create(self.test_user_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/friendships/{user_id!s}/follow/'.format(**{'user_id': self.test_user_id}),
            params='')

    @unittest.skip('Modifies data')
    def test_friendships_destroy(self):
        results = self.api.friendships_destroy(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_friendships_destroy_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.friendships_destroy(self.test_user_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/friendships/{user_id!s}/unfollow/'.format(**{'user_id': self.test_user_id}),
            params='')
