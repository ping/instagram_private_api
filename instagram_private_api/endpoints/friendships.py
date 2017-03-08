from ..compat import compat_urllib_parse
from ..compatpatch import ClientCompatPatch


class FriendshipsEndpointsMixin(object):

    def autocomplete_user_list(self):
        """User list for autocomplete"""
        endpoint = 'friendships/autocomplete_user_list/?' + compat_urllib_parse.urlencode(
            {'followinfo': 'True', 'version': '2'})
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(user, drop_incompat_keys=self.drop_incompat_keys)
             for user in res['users']]
        return res

    def user_following(self, user_id, **kwargs):
        """
        Get user followings

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        endpoint = 'friendships/%(user_id)s/following/?' % {'user_id': user_id}
        default_params = {
            'rank_token': self.rank_token,
        }
        params = default_params.copy()
        if kwargs:
            params.update(kwargs)
        endpoint += compat_urllib_parse.urlencode(params)
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def user_followers(self, user_id, **kwargs):
        """
        Get user followers

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        endpoint = 'friendships/%(user_id)s/followers/?' % {'user_id': user_id}
        default_params = {
            'rank_token': self.rank_token,
        }
        params = default_params.copy()
        if kwargs:
            params.update(kwargs)
        endpoint += compat_urllib_parse.urlencode(params)
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def friendships_pending(self):
        """Get pending follow requests"""
        res = self._call_api('friendships/pending/')
        if self.auto_patch and res.get('users'):
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def friendships_show(self, user_id):
        """
        Get friendship status with user id

        :param user_id:
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "incoming_request": false,
                    "is_blocking_reel": false,
                    "followed_by": false,
                    "is_muting_reel": false,
                    "outgoing_request": false,
                    "following": false,
                    "blocking": false,
                    "is_private": false
                }
        """
        endpoint = 'friendships/show/%(user_id)s/' % {'user_id': user_id}
        res = self._call_api(endpoint)
        return res

    def friendships_show_many(self, user_ids):
        """
        Get friendship status with mulitple user ids

        :param user_ids: list of user ids
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "friendship_statuses": {
                        "123456789": {
                            "following": false,
                            "incoming_request": true,
                            "outgoing_request": false,
                            "is_private": false
                        }
                    }
                }
        """
        if isinstance(user_ids, str):
            user_ids = [user_ids]

        endpoint = 'friendships/show_many/'
        params = {
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken,
            'user_ids': ','.join(user_ids)
        }
        res = self._call_api(endpoint, params=params, unsigned=True)
        return res

    def friendships_create(self, user_id):
        """
        Follow a user

        :param user_id: User id
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "friendship_status": {
                        "incoming_request": false,
                        "followed_by": false,
                        "outgoing_request": false,
                        "following": true,
                        "blocking": false,
                        "is_private": false
                    }
                }
        """
        endpoint = 'friendships/create/%(user_id)s/' % {'user_id': user_id}
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def friendships_destroy(self, user_id, **kwargs):
        """
        Unfollow a user

        :param user_id: User id
        :param kwargs:
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "incoming_request": false,
                    "is_blocking_reel": false,
                    "followed_by": false,
                    "is_muting_reel": false,
                    "outgoing_request": false,
                    "following": false,
                    "blocking": false,
                    "is_private": false
                }
        """
        endpoint = 'friendships/destroy/%(user_id)s/' % {'user_id': user_id}
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def friendships_block(self, user_id):
        """
        Block a user

        :param user_id: User id
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "incoming_request": false,
                    "is_blocking_reel": false,
                    "followed_by": false,
                    "is_muting_reel": false,
                    "outgoing_request": false,
                    "following": false,
                    "blocking": true,
                    "is_private": false
                }
        """
        endpoint = 'friendships/block/%(user_id)s/' % {'user_id': user_id}
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res
