import warnings

from .common import ClientExperimentalWarning, ClientDeprecationWarning
from ..compatpatch import ClientCompatPatch


class UsersEndpointsMixin(object):
    """For endpoints in ``/users/``."""

    def user_info(self, user_id):
        """
        Get user info for a specified user id

        :param user_id:
        :return:
        """
        res = self._call_api('users/{user_id!s}/info/'.format(**{'user_id': user_id}))
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def username_info(self, user_name):
        """
        Get user info for a specified user name
        :param user_name:
        :return:
        """
        res = self._call_api('users/{user_name!s}/usernameinfo/'.format(**{'user_name': user_name}))
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def user_detail_info(self, user_id, **kwargs):
        """
        EXPERIMENTAL ENDPOINT, INADVISABLE TO USE.
        Get user detailed info

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
            - **min_timestamp**: For pagination
        :return:
        """
        warnings.warn('This endpoint is experimental. Do not use.', ClientExperimentalWarning)

        endpoint = 'users/{user_id!s}/full_detail_info/'.format(**{'user_id': user_id})
        res = self._call_api(endpoint, query=kwargs)
        if self.auto_patch:
            ClientCompatPatch.user(res['user_detail']['user'], drop_incompat_keys=self.drop_incompat_keys)
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('feed', {}).get('items', [])]
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('reel_feed', {}).get('items', [])]
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('user_story', {}).get('reel', {}).get('items', [])]
        return res

    def user_map(self, user_id):    # pragma: no cover
        """
        Get a list of geo-tagged media from a user

        :param user_id: User id
        :return:
        """
        warnings.warn(
            'This endpoint is believed to be obsolete. Do not use.',
            ClientDeprecationWarning)

        endpoint = 'maps/user/{user_id!s}/'.format(**{'user_id': user_id})
        return self._call_api(endpoint)

    def search_users(self, query, **kwargs):
        """
        Search users

        :param query: Search string
        :return:
        """
        query_params = {
            'q': query,
            'timezone_offset': self.timezone_offset,
            'count': 50,
        }
        query_params.update(kwargs)
        res = self._call_api('users/search/', query=query_params)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def check_username(self, username):
        """
        Check username

        :param username:
        :return:
            .. code-block:: javascript

                {
                  "status": "ok",
                  "available": false,
                  "username": "xxx",
                  "error_type": "username_is_taken",
                  "error": "The username xxx is not available."
                }
        """
        params = {'username': username}
        return self._call_api('users/check_username/', params=params)

    def blocked_user_list(self):
        """
        Get list of blocked users

        """
        return self._call_api('users/blocked_list/')

    def user_reel_settings(self):
        """
        Get user reel settings
        """
        res = self._call_api('users/reel_settings/')
        if self.auto_patch and res.get('blocked_reels', {}).get('users'):
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('blocked_reels', {}).get('users', [])]
        return res

    def set_reel_settings(
            self, message_prefs,
            allow_story_reshare=None, reel_auto_archive=None,
            save_to_camera_roll=None):
        """
        Set story message replies settings

        :param message_prefs: One of 'anyone', 'following', 'off'
        :param allow_story_reshare: bool
        :param auto_archive: One of 'on', 'off'
        :param save_to_camera_roll: bool
        :return:
            .. code-block:: javascript

                {
                    "message_prefs": "off",
                    "status": "ok"
                }
        """
        if message_prefs not in ['anyone', 'following', 'off']:
            raise ValueError('Invalid message_prefs: {0!s}'.format(message_prefs))
        params = {'message_prefs': message_prefs}
        if allow_story_reshare is not None:
            params['allow_story_reshare'] = '1' if allow_story_reshare else '0'
        if reel_auto_archive is not None:
            if reel_auto_archive not in ['on', 'off']:
                raise ValueError('Invalid auto_archive: {0!s}'.format(reel_auto_archive))
            params['reel_auto_archive'] = reel_auto_archive
        if save_to_camera_roll is not None:
            params['save_to_camera_roll'] = '1' if save_to_camera_roll else '0'
        params.update(self.authenticated_params)
        return self._call_api('users/set_reel_settings/', params=params)
