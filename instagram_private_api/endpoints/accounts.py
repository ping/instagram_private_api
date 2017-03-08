import json

from ..compat import compat_urllib_request, compat_urllib_error
from ..errors import ClientError
from ..http import MultipartFormDataEncoder
from ..compatpatch import ClientCompatPatch


class AccountsEndpointsMixin(object):

    def current_user(self):
        """Get current user info"""
        endpoint = 'accounts/current_user/?edit=true'
        params = self.authenticated_params
        res = self._call_api(endpoint, params=params)
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
            raise ValueError('Invalid gender: %d' % int(gender))
        if not email:
            raise ValueError('Email is required.')

        endpoint = 'accounts/edit_profile/'
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
        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            ClientCompatPatch.user(res.get('user'))
        return res

    def remove_profile_picture(self):
        """Remove profile picture"""
        endpoint = 'accounts/remove_profile_picture/'
        res = self._call_api(endpoint, params=self.authenticated_params)
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

        content_type, body = MultipartFormDataEncoder(self.uuid).encode(fields, files)

        headers = self.default_headers
        headers['Content-Type'] = content_type
        headers['Content-Length'] = len(body)

        req = compat_urllib_request.Request(self.api_url + endpoint, body, headers=headers)
        try:
            response = self.opener.open(req, timeout=self.timeout)
        except compat_urllib_error.HTTPError as e:
            error_msg = e.reason
            error_response = e.read()
            try:
                error_obj = json.loads(error_response)
                if error_obj.get('message'):
                    error_msg = '%s: %s' % (e.reason, error_obj['message'])
            except:
                # do nothing, prob can't parse json
                pass
            raise ClientError(error_msg, e.code, error_response)

        json_response = json.loads(self._read_response(response))

        if self.auto_patch:
            ClientCompatPatch.user(json_response['user'], drop_incompat_keys=self.drop_incompat_keys)

        return json_response

    def set_account_private(self):
        """Make account private"""
        endpoint = 'accounts/set_private/'
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def set_account_public(self):
        """Make account public"""""
        endpoint = 'accounts/set_public/'
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def logout(self):
        """Logout user"""
        endpoint = 'accounts/logout/'
        params = {
            'phone_id': self.phone_id,
            '_csrftoken': self.csrftoken,
            'guid': self.uuid,
            'device_id': self.device_id,
            '_uuid': self.uuid
        }
        return self._call_api(endpoint, params=params, unsigned=True)
