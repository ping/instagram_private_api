import json

from ..compat import compat_urllib_request, compat_urllib_error
from ..errors import ClientError, ClientLoginError
from ..http import MultipartFormDataEncoder
from ..compatpatch import ClientCompatPatch


class AccountsEndpointsMixin(object):
    """For endpoints in ``/accounts/``."""

    def login(self):
        """Login."""
        challenge_response = self._call_api(
            'si/fetch_headers/',
            params='',
            query={'challenge_type': 'signup', 'guid': self.generate_uuid(True)},
            return_response=True)

        if not self.csrftoken:
            raise ClientError(
                'Unable to get csrf from login challenge.',
                error_response=self._read_response(challenge_response))

        login_params = {
            'device_id': self.device_id,
            'guid': self.uuid,
            'adid': self.ad_id,
            'phone_id': self.phone_id,
            '_csrftoken': self.csrftoken,
            'username': self.username,
            'password': self.password,
            'login_attempt_count': '0',
        }

        try:
            login_response = self._call_api(
                'accounts/login/', params=login_params, return_response=True)
        except compat_urllib_error.HTTPError as e:
            error_response = self._read_response(e)
            if e.code == 400:
                raise ClientLoginError('Unable to login: {0!s}'.format(e))
            raise ClientError(e.reason, e.code, error_response)

        if not self.csrftoken:
            raise ClientError(
                'Unable to get csrf from login.',
                error_response=self._read_response(login_response))

        login_json = json.loads(self._read_response(login_response))

        if not login_json.get('logged_in_user', {}).get('pk'):
            raise ClientLoginError('Unable to login.')

        if self.on_login:
            on_login_callback = self.on_login
            on_login_callback(self)

        # # Post-login calls in client
        # self.sync()
        # self.autocomplete_user_list()
        # self.feed_timeline()
        # self.ranked_recipients()
        # self.recent_recipients()
        # self.direct_v2_inbox()
        # self.news_inbox()
        # self.explore()

    def current_user(self):
        """Get current user info"""
        params = self.authenticated_params
        res = self._call_api('accounts/current_user/', params=params, query={'edit': 'true'})
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def edit_profile(self, first_name, biography, external_url, email, phone_number, gender):
        """
        Edit profile

        :param first_name:
        :param biography:
        :param external_url:
        :param email: Required.
        :param phone_number:
        :param gender: male: 1, female: 2, unspecified: 3
        :return:
        """
        if int(gender) not in [1, 2, 3]:
            raise ValueError('Invalid gender: {0:d}'.format(int(gender)))
        if not email:
            raise ValueError('Email is required.')

        params = {
            'username': self.authenticated_user_name,
            'gender': int(gender),
            'phone_number': phone_number or '',
            'first_name': first_name or '',
            'biography': biography or '',
            'external_url': external_url or '',
            'email': email,
        }
        params.update(self.authenticated_params)
        res = self._call_api('accounts/edit_profile/', params=params)
        if self.auto_patch:
            ClientCompatPatch.user(res.get('user'))
        return res

    def remove_profile_picture(self):
        """Remove profile picture"""
        res = self._call_api(
            'accounts/remove_profile_picture/', params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def change_profile_picture(self, photo_data):
        """
        Change profile picture

        :param photo_data: byte string of image
        :return:
        """
        endpoint = 'accounts/change_profile_picture/'
        json_params = json.dumps(self.authenticated_params)
        hash_sig = self._generate_signature(json_params)
        fields = [
            ('ig_sig_key_version', self.key_version),
            ('signed_body', hash_sig + '.' + json_params)
        ]
        files = [
            ('profile_pic', 'profile_pic', 'application/octet-stream', photo_data)
        ]

        content_type, body = MultipartFormDataEncoder().encode(fields, files)

        headers = self.default_headers
        headers['Content-Type'] = content_type
        headers['Content-Length'] = len(body)

        endpoint_url = '{0}{1}'.format(self.api_url.format(version='v1'), endpoint)
        req = compat_urllib_request.Request(endpoint_url, body, headers=headers)
        try:
            self.logger.debug('POST {0!s}'.format(endpoint_url))
            response = self.opener.open(req, timeout=self.timeout)
        except compat_urllib_error.HTTPError as e:
            error_msg = e.reason
            error_response = self._read_response(e)
            self.logger.debug('RESPONSE: {0:d} {1!s}'.format(e.code, error_response))
            try:
                error_obj = json.loads(error_response)
                if error_obj.get('message'):
                    error_msg = '{0!s}: {1!s}'.format(e.reason, error_obj['message'])
            except Exception as e:
                # do nothing else, prob can't parse json
                self.logger.warn('Error parsing error response: {}'.format(str(e)))
            raise ClientError(error_msg, e.code, error_response)

        post_response = self._read_response(response)
        self.logger.debug('RESPONSE: {0:d} {1!s}'.format(response.code, post_response))
        json_response = json.loads(post_response)

        if self.auto_patch:
            ClientCompatPatch.user(json_response['user'], drop_incompat_keys=self.drop_incompat_keys)

        return json_response

    def set_account_private(self):
        """Make account private"""
        res = self._call_api('accounts/set_private/', params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def set_account_public(self):
        """Make account public"""""
        res = self._call_api('accounts/set_public/', params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def logout(self):
        """Logout user"""
        params = {
            'phone_id': self.phone_id,
            '_csrftoken': self.csrftoken,
            'guid': self.uuid,
            'device_id': self.device_id,
            '_uuid': self.uuid
        }
        return self._call_api('accounts/logout/', params=params, unsigned=True)
