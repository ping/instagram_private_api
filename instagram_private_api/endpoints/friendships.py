import warnings

from .common import ClientExperimentalWarning
from ..compatpatch import ClientCompatPatch
from ..utils import raise_if_invalid_rank_token


class FriendshipsEndpointsMixin(object):
    """For endpoints in ``/friendships/``."""

    def autocomplete_user_list(self):
        """User list for autocomplete"""
        res = self._call_api(
            'friendships/autocomplete_user_list/',
            query={'followinfo': 'True', 'version': '2'})
        if self.auto_patch:
            [ClientCompatPatch.list_user(user, drop_incompat_keys=self.drop_incompat_keys)
             for user in res['users']]
        return res

    def user_following(self, user_id, rank_token, **kwargs):
        """
        Get user followings

        :param user_id:
        :param rank_token: Required for paging through a single feed and can be generated with
            :meth:`generate_uuid`. You should use the same rank_token for paging through a single user following.
        :param kwargs:
            - **query**: Search within the user following
            - **max_id**: For pagination
        :return:
        """
        raise_if_invalid_rank_token(rank_token)

        endpoint = 'friendships/{user_id!s}/following/'.format(**{'user_id': user_id})
        query_params = {
            'rank_token': rank_token,
        }
        query_params.update(kwargs)
        res = self._call_api(endpoint, query=query_params)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def user_followers(self, user_id, rank_token, **kwargs):
        """
        Get user followers

        :param user_id:
        :param rank_token: Required for paging through a single feed and can be generated with
            :meth:`generate_uuid`. You should use the same rank_token for paging through a single user followers.
        :param kwargs:
            - **query**: Search within the user followers
            - **max_id**: For pagination
        :return:
        """
        raise_if_invalid_rank_token(rank_token)

        endpoint = 'friendships/{user_id!s}/followers/'.format(**{'user_id': user_id})
        query_params = {
            'rank_token': rank_token,
        }
        query_params.update(kwargs)
        res = self._call_api(endpoint, query=query_params)
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
        endpoint = 'friendships/show/{user_id!s}/'.format(**{'user_id': user_id})
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

        params = {
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken,
            'user_ids': ','.join(user_ids)
        }
        res = self._call_api('friendships/show_many/', params=params, unsigned=True)
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
        endpoint = 'friendships/create/{user_id!s}/'.format(**{'user_id': user_id})
        params = {'user_id': user_id, 'radio_type': self.radio_type}
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
        endpoint = 'friendships/destroy/{user_id!s}/'.format(**{'user_id': user_id})
        params = {'user_id': user_id, 'radio_type': self.radio_type}
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
        endpoint = 'friendships/block/{user_id!s}/'.format(**{'user_id': user_id})
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def friendships_unblock(self, user_id):
        """
        Unblock a user

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
                    "blocking": false,
                    "is_private": false
                }
        """
        endpoint = 'friendships/unblock/{user_id!s}/'.format(**{'user_id': user_id})
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def block_friend_reel(self, user_id):
        """
        Hide your stories from a specific user

        :param user_id: User id
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "incoming_request": false,
                    "is_blocking_reel": true,
                    "followed_by": false,
                    "is_muting_reel": false,
                    "outgoing_request": false,
                    "following": false,
                    "blocking": true,
                    "is_private": false
                }
        """
        endpoint = 'friendships/block_friend_reel/{user_id!s}/'.format(**{'user_id': user_id})
        params = {'source': 'main_feed'}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def unblock_friend_reel(self, user_id):
        """
        Unhide your stories from a specific user

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
        endpoint = 'friendships/unblock_friend_reel/{user_id!s}/'.format(**{'user_id': user_id})
        res = self._call_api(endpoint, params=self.authenticated_params)
        return res

    def set_reel_block_status(self, user_ids, block_status='block'):
        """
        Unhide your stories from a specific user

        :param user_ids: list of user IDs
        :param block_status: One of 'block', 'unblock'
        :return:
            .. code-block:: javascript

                {
                    "friendship_statuses": {
                        "123456790": {
                            "following": true,
                            "is_private": false,
                            "incoming_request": false,
                            "outgoing_request": false,
                            "is_blocking_reel": true,
                            "is_muting_reel": false
                        },
                        "123456791": {
                            "following": true,
                            "is_private": false,
                            "incoming_request": false,
                            "outgoing_request": false,
                            "is_blocking_reel": true,
                            "is_muting_reel": false
                        }
                    },
                    "status": "ok"
                }
        """

        if block_status not in ['block', 'unblock']:
            raise ValueError('Invalid block_status: {0!s}'.format(block_status))
        if not isinstance(user_ids, list):
            user_ids = [user_ids]
        params = {'source': 'settings'}
        user_block_statuses = {}
        for user_id in user_ids:
            user_block_statuses[str(user_id)] = block_status
        params['user_block_statuses'] = user_block_statuses
        params.update(self.authenticated_params)
        return self._call_api('friendships/set_reel_block_status/', params=params)

    def blocked_reels(self):
        """
        Get list of users from whom you've hid your stories
        """
        warnings.warn('This endpoint is experimental. Do not use.', ClientExperimentalWarning)
        res = self._call_api('friendships/blocked_reels/', params=self.authenticated_params)
        if self.auto_patch and res.get('users'):
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def enable_post_notifications(self, user_id):
        """
        Turn on post notifications for specified user.

        :param user_id:
        :return:
        """
        res = self._call_api(
            'friendships/favorite/{user_id!s}/'.format(**{'user_id': user_id}),
            params=self.authenticated_params)
        return res

    def disable_post_notifications(self, user_id):
        """
        Turn off post notifications for specified user.

        :param user_id:
        :return:
        """
        res = self._call_api(
            'friendships/unfavorite/{user_id!s}/'.format(**{'user_id': user_id}),
            params=self.authenticated_params)
        return res

    def ignore_user(self, user_id):
        """
        Ignore a user's follow request.

        :param user_id:
        :return:
        """
        params = {'user_id': user_id, 'radio_type': self.radio_type}
        params.update(self.authenticated_params)
        res = self._call_api(
            'friendships/ignore/{user_id!s}/'.format(**{'user_id': user_id}),
            params=params)
        return res

    def remove_follower(self, user_id):
        """
        Remove a follower.

        :param user_id:
        :return:
        """
        params = {'user_id': user_id, 'radio_type': self.radio_type}
        params.update(self.authenticated_params)
        res = self._call_api(
            'friendships/remove_follower/{user_id!s}/'.format(**{'user_id': user_id}),
            params=params)
        return res
