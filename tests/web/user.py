import unittest

from ..common import WebApiTestBase, WebClientError as ClientError, compat_mock


class UserTests(WebApiTestBase):

    @classmethod
    def init_all(cls, api):
        return [
            {
                'name': 'test_user_info',
                'test': UserTests('test_user_info', api),
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
                'name': 'test_user_feed_extract',
                'test': UserTests('test_user_feed_extract', api)
            },
            {
                'name': 'test_user_followers',
                'test': UserTests('test_user_followers', api),
                'require_auth': True,
            },
            {
                'name': 'test_user_followers_extract',
                'test': UserTests('test_user_followers_extract', api),
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

    def test_user_info(self):
        results = self.api.user_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('profile_picture'))

    def test_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
        self.assertGreater(len(results), 0)

    def test_notfound_user_feed(self):
        self.assertRaises(ClientError, lambda: self.api.user_feed('1'))

    def test_user_feed_extract(self, extract=True):
        results = self.api.user_feed(self.test_user_id)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], dict)

    def test_user_followers(self):
        results = self.api.user_followers(self.test_user_id)
        self.assertGreater(len(results), 0)

    def test_user_followers_extract(self):
        results = self.api.user_followers(self.test_user_id, extract=True)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_user_following(self):
        results = self.api.user_following(self.test_user_id)
        self.assertGreater(len(results), 0)

    @unittest.skip('Modifies data')
    def test_friendships_create(self):
        results = self.api.friendships_create(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_friendships_create_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.friendships_create(self.test_user_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/friendships/%(user_id)s/follow/' % {'user_id': self.test_user_id},
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
            'https://www.instagram.com/web/friendships/%(user_id)s/unfollow/' % {'user_id': self.test_user_id},
            params='')
