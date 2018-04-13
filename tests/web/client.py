
from ..common import (
    WebApiTestBase, WebClientError as ClientError,
    WebClientLoginError as ClientLoginError,
    WebClient as Client,
    compat_mock, compat_urllib_error
)


class ClientTests(WebApiTestBase):
    """Tests for client related functions."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_search',
                'test': ClientTests('test_search', api),
            },
            {
                'name': 'test_client_properties',
                'test': ClientTests('test_client_properties', api),
                'require_auth': True,
            },
            {
                'name': 'test_client_errors',
                'test': ClientTests('test_client_errors', api)
            },
            {
                'name': 'test_client_init',
                'test': ClientTests('test_client_init', api)
            },
            {
                'name': 'test_login_mock',
                'test': ClientTests('test_login_mock', api)
            },
            {
                'name': 'test_unauthed_client',
                'test': ClientTests('test_unauthed_client', api)
            }
        ]

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_login_mock(self, make_request):
        make_request.side_effect = [
            {'status': 'ok', 'authenticated': 'x'},
            {'status': 'fail'}
        ]
        self.api.on_login = lambda x: self.assertIsNotNone(x)
        self.api.login()
        self.api.on_login = None

        make_request.assert_called_with(
            'https://www.instagram.com/accounts/login/ajax/',
            params={
                'username': self.api.username,
                'password': self.api.password,
                'queryParams': '{}'})
        with self.assertRaises(ClientLoginError):
            self.api.login()

    def test_search(self):
        results = self.api.search('maru')
        self.assertGreaterEqual(len(results['users']), 0)
        self.assertGreaterEqual(len(results['hashtags']), 0)

    def test_client_properties(self):
        self.sleep_interval = 0
        self.assertIsNotNone(self.api.csrftoken)
        self.assertIsNotNone(self.api.authenticated_user_id)
        self.assertTrue(self.api.is_authenticated)
        settings = self.api.settings
        for k in ('cookie', 'created_ts'):
            self.assertIsNotNone(settings.get(k))
        self.assertIsNotNone(self.api.cookie_jar.dump())

    @compat_mock.patch('instagram_web_api.client.compat_urllib_request.OpenerDirector.open')
    def test_client_errors(self, open_mock):
        self.sleep_interval = 0
        open_mock.side_effect = [
            compat_urllib_error.HTTPError('', 404, 'Not Found', None, None),
            compat_urllib_error.URLError('No route to host')]

        with self.assertRaises(ClientError):
            self.api.search('maru')

        with self.assertRaises(ClientError):
            self.api.search('maru')

    @compat_mock.patch('instagram_web_api.Client.csrftoken',
                       new_callable=compat_mock.PropertyMock, return_value=None)
    def test_client_init(self, csrftoken):
        with self.assertRaises(ClientError):
            self.api.init()

    def test_unauthed_client(self):
        api = Client()
        self.assertFalse(api.is_authenticated)

        with self.assertRaises(ClientError):
            # Test authenticated method
            api.user_following(self.test_user_id)
