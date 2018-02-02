import unittest
import json
try:
    # python 2.x
    from urllib2 import urlopen
except ImportError:
    # python 3.x
    from urllib.request import urlopen
from io import BytesIO

from ..common import (
    Client, ClientError, ClientLoginError,
    ApiTestBase, compat_mock, compat_urllib_error, MockResponse
)


class AccountTests(ApiTestBase):
    """Tests for AccountsEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_login',
                'test': AccountTests('test_login', api)
            },
            {
                'name': 'test_login_mock',
                'test': AccountTests('test_login_mock', api)
            },
            {
                'name': 'test_login_failcsrf_mock',
                'test': AccountTests('test_login_failcsrf_mock', api)
            },
            {
                'name': 'test_login_fail_mock',
                'test': AccountTests('test_login_fail_mock', api)
            },
            {
                'name': 'test_remove_profile_picture',
                'test': AccountTests('test_remove_profile_picture', api)
            },
            {
                'name': 'test_remove_profile_picture_mock',
                'test': AccountTests('test_remove_profile_picture_mock', api)
            },
            {
                'name': 'test_set_account_public',
                'test': AccountTests('test_set_account_public', api)
            },
            {
                'name': 'test_set_account_public_mock',
                'test': AccountTests('test_set_account_public_mock', api)
            },
            {
                'name': 'test_set_account_private',
                'test': AccountTests('test_set_account_private', api)
            },
            {
                'name': 'test_set_account_private_mock',
                'test': AccountTests('test_set_account_private_mock', api)
            },
            {
                'name': 'test_change_profile_picture',
                'test': AccountTests('test_change_profile_picture', api)
            },
            {
                'name': 'test_current_user',
                'test': AccountTests('test_current_user', api)
            },
            {
                'name': 'test_edit_profile',
                'test': AccountTests('test_edit_profile', api)
            },
            {
                'name': 'test_edit_profile_mock',
                'test': AccountTests('test_edit_profile_mock', api)
            },
            {
                'name': 'test_logout',
                'test': AccountTests('test_logout', api)
            },
            {
                'name': 'test_logout_mock',
                'test': AccountTests('test_logout_mock', api)
            },
            {
                'name': 'test_change_profile_picture_mock',
                'test': AccountTests('test_change_profile_picture_mock', api)
            },
            {
                'name': 'test_presence_status',
                'test': AccountTests('test_presence_status', api)
            },
            {
                'name': 'test_enable_presence_status_mock',
                'test': AccountTests('test_enable_presence_status_mock', api)
            },
            {
                'name': 'test_disable_presence_status_mock',
                'test': AccountTests('test_disable_presence_status_mock', api)
            },
        ]

    @unittest.skip('Unwise to run frequently.')
    def test_login(self):
        new_client = Client(self.api.username, self.api.password)
        self.assertEqual(new_client.authenticated_user_name, self.api.username)

    @compat_mock.patch('instagram_private_api.Client.csrftoken',
                       new_callable=compat_mock.PropertyMock, return_value='abcde')
    def test_login_mock(self, csrftoken):
        generated_uuid = Client.generate_uuid(True)
        query = {'challenge_type': 'signup', 'guid': generated_uuid}
        with compat_mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock, \
                compat_mock.patch('instagram_private_api.Client._call_api') as call_api, \
                compat_mock.patch('instagram_private_api.Client._read_response') as read_response:
            generate_uuid_mock.return_value = generated_uuid
            call_api.return_value = ''
            read_response.return_value = json.dumps({'status': 'ok', 'logged_in_user': {'pk': 123}})

            self.api.on_login = lambda x: self.assertIsNotNone(x)
            self.api.login()

            call_api.assert_any_call(
                'si/fetch_headers/', params='', query=query, return_response=True)

            login_params = {
                'device_id': self.api.device_id,
                'guid': self.api.uuid,
                'adid': self.api.ad_id,
                'phone_id': self.api.phone_id,
                '_csrftoken': self.api.csrftoken,
                'username': self.api.username,
                'password': self.api.password,
                'login_attempt_count': '0',
            }
            call_api.assert_called_with(
                'accounts/login/', params=login_params, return_response=True)

    @compat_mock.patch('instagram_private_api.Client.csrftoken',
                       new_callable=compat_mock.PropertyMock, return_value=None)
    def test_login_failcsrf_mock(self, csrftoken):
        generated_uuid = Client.generate_uuid(True)
        with compat_mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock, \
                compat_mock.patch('instagram_private_api.Client._call_api') as call_api, \
                compat_mock.patch('instagram_private_api.Client._read_response') as read_response:
            generate_uuid_mock.return_value = generated_uuid
            call_api.return_value = ''
            read_response.return_value = ''
            with self.assertRaises(ClientError) as tc:
                self.api.login()
            self.assertEqual(tc.exception.msg, 'Unable to get csrf from prelogin.')

    @compat_mock.patch('instagram_private_api.Client.csrftoken',
                       new_callable=compat_mock.PropertyMock, return_value='abcde')
    def test_login_fail_mock(self, csrftoken):
        generated_uuid = Client.generate_uuid(True)
        with compat_mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock, \
                compat_mock.patch('instagram_private_api.Client._call_api') as call_api, \
                compat_mock.patch('instagram_private_api.Client._read_response') as read_response:
            generate_uuid_mock.return_value = generated_uuid
            call_api.side_effect = [
                '',     # Test 1
                '',     # Test 1
                '',     # Test 2
                ClientError(        # Test 2
                    'Internal Server Error', code=500,
                    error_response='Internal Server Error'),
                '',     # Test 3
                ClientLoginError(       # Test 2
                    'Invalid', code=400,
                    error_response='Invalid'),
            ]
            read_response.return_value = json.dumps({'status': 'fail'})

            # Test 1
            with self.assertRaises(ClientError) as ce:
                self.api.login()
            self.assertEqual(ce.exception.msg, 'Unable to login.')

            # Test 2
            with self.assertRaises(ClientError) as ce:
                self.api.login()
            self.assertEqual(ce.exception.msg, 'Internal Server Error')

            # Test 3
            with self.assertRaises(ClientError) as cle:
                self.api.login()
            self.assertEqual(cle.exception.msg, 'Invalid')

    def test_current_user(self):
        results = self.api.current_user()
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(str(results.get('user', {}).get('pk', '')), self.api.authenticated_user_id)

    @unittest.skip('Modifies data.')
    def test_edit_profile(self):
        user = self.api.current_user()['user']
        results = self.api.edit_profile(
            first_name=user['full_name'],
            biography=user['biography'] + ' <3',
            external_url=user['external_url'],
            email=user['email'],
            phone_number=user['phone_number'],
            gender=user['gender']
        )
        self.assertEqual(results.get('status'), 'ok')
        returned_user = results['user']
        self.assertEqual(returned_user['full_name'], user['full_name'])
        self.assertEqual(returned_user['biography'], user['biography'] + ' <3')
        self.assertEqual(returned_user['external_url'], user['external_url'])
        self.assertEqual(returned_user['email'], user['email'])
        self.assertEqual(returned_user['phone_number'], user['phone_number'])
        self.assertEqual(returned_user['gender'], user['gender'])

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_edit_profile_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}

        params = {
            'username': self.api.authenticated_user_name,
            'gender': 1,
            'phone_number': '',
            'first_name': '',
            'biography': '',
            'external_url': '',
            'email': 'john@example.com',
        }
        params.update(self.api.authenticated_params)
        self.api.edit_profile(
            first_name=params['first_name'],
            biography=params['biography'],
            external_url=params['external_url'],
            email=params['email'],
            phone_number=params['phone_number'],
            gender=params['gender']
        )
        call_api.assert_called_with(
            'accounts/edit_profile/',
            params=params)

        with self.assertRaises(ValueError):
            self.api.edit_profile(
                first_name='',
                biography='',
                external_url='',
                email='x@example.com',
                gender='9',
                phone_number=''
            )
        with self.assertRaises(ValueError):
            self.api.edit_profile(
                first_name='',
                biography='',
                external_url='',
                email='',
                gender='1',
                phone_number=''
            )

    @unittest.skip('Modifies data.')
    def test_remove_profile_picture(self):
        results = self.api.remove_profile_picture()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_remove_profile_picture_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}
        self.api.remove_profile_picture()
        call_api.assert_called_with(
            'accounts/remove_profile_picture/',
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_change_profile_picture(self):
        sample_url = 'https://c2.staticflickr.com/8/7162/6461496097_fdb8d1f7cc_b.jpg'
        res = urlopen(sample_url)
        photo_data = res.read()
        results = self.api.change_profile_picture(photo_data)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @unittest.skip('Modifies data.')
    def test_set_account_public(self):
        results = self.api.set_account_public()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_set_account_public_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}
        self.api.set_account_public()
        call_api.assert_called_with(
            'accounts/set_public/',
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_set_account_private(self):
        results = self.api.set_account_private()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_set_account_private_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}
        self.api.set_account_private()
        call_api.assert_called_with(
            'accounts/set_private/',
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_logout(self):
        results = self.api.logout()
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_logout_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        self.api.logout()
        call_api.assert_called_with(
            'accounts/logout/',
            params={
                'phone_id': self.api.phone_id,
                '_csrftoken': self.api.csrftoken,
                'guid': self.api.uuid,
                'device_id': self.api.device_id,
                '_uuid': self.api.uuid
            },
            unsigned=True)

    @compat_mock.patch('instagram_private_api.endpoints.accounts.compat_urllib_request.OpenerDirector.open')
    def test_change_profile_picture_mock(self, opener):
        opener.side_effect = [
            MockResponse(),
            compat_urllib_error.HTTPError(
                self.api.api_url, 500, 'Internal Server Error', {},
                BytesIO('Internal Server Error'.encode('utf-8')))
        ]
        with compat_mock.patch('instagram_private_api.Client._read_response') as read_response, \
                compat_mock.patch('instagram_private_api.Client.default_headers') as default_headers, \
                compat_mock.patch('instagram_private_api.endpoints.accounts.compat_urllib_request.Request') \
                as request, \
                compat_mock.patch('instagram_private_api.http.random.choice') as randchoice_mock:
            default_headers.return_value = {'Header': 'X'}
            randchoice_mock.return_value = 'x'
            read_response.return_value = json.dumps(
                {'status': 'ok',
                 'user': {'pk': 123, 'biography': '', 'profile_pic_url': '', 'external_url': ''}})

            photo_data = '...'.encode('ascii')
            json_params = json.dumps(self.api.authenticated_params)
            hash_sig = self.api._generate_signature(json_params)
            signed_body = hash_sig + '.' + json_params
            headers = self.api.default_headers
            headers.update({
                'Content-Type': 'multipart/form-data; boundary={0!s}'.format(self.api.uuid),
                'Content-Length': len(photo_data)
            })
            body = '--%(boundary)s\r\n' \
                   'Content-Disposition: form-data; name="ig_sig_key_version"\r\n\r\n' \
                   '%(sig_version)s\r\n' \
                   '--%(boundary)s\r\n' \
                   'Content-Disposition: form-data; name="signed_body"\r\n\r\n' \
                   '%(signed_body)s\r\n' \
                   '--%(boundary)s\r\n' \
                   'Content-Disposition: form-data; name="profile_pic"; filename="profile_pic"\r\n' \
                   'Content-Type: application/octet-stream\r\n' \
                   'Content-Transfer-Encoding: binary\r\n\r\n...\r\n' \
                   '--%(boundary)s--\r\n' % {
                       'boundary': 'x' * 30,
                       'signed_body': signed_body,
                       'sig_version': self.api.key_version
                   }

            self.api.change_profile_picture(photo_data)
            endpoint_url = '{0}{1}'.format(self.api.api_url.format(version='v1'), 'accounts/change_profile_picture/')
            request.assert_called_with(
                endpoint_url, body.encode('ascii'), headers=headers)

            with self.assertRaises(ClientError) as he:
                self.api.change_profile_picture(photo_data)
            self.assertEqual(str(he.exception), 'Internal Server Error')

    def test_presence_status(self):
        results = self.api.presence_status()
        self.assertIn('disabled', results)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_enable_presence_status_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        self.api.enable_presence_status()
        call_api.assert_called_with(
            'accounts/set_presence_disabled/',
            params={
                '_csrftoken': self.api.csrftoken,
                '_uuid': self.api.uuid,
                '_uid': self.api.authenticated_user_id,
                'disabled': '0',
            })

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_disable_presence_status_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        self.api.disable_presence_status()
        call_api.assert_called_with(
            'accounts/set_presence_disabled/',
            params={
                '_csrftoken': self.api.csrftoken,
                '_uuid': self.api.uuid,
                '_uid': self.api.authenticated_user_id,
                'disabled': '1',
            })
