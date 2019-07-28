from ..compatpatch import ClientCompatPatch


class UsertagsEndpointsMixin(object):
    """For endpoints in ``/usertags/``."""

    def usertag_feed(self, user_id, **kwargs):
        """
        Get a usertag feed

        :param user_id:
        :param kwargs:
        :return:
        """
        endpoint = 'usertags/{user_id!s}/feed/'.format(**{'user_id': user_id})
        query = {'rank_token': self.rank_token, 'ranked_content': 'true'}
        query.update(kwargs)
        res = self._call_api(endpoint, query=query)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def usertag_self_remove(self, media_id):
        """
        Remove your own user tag from a media post

        :param media_id: Media id
        :return:
        """
        endpoint = 'usertags/{media_id!s}/remove/'.format(**{'media_id': media_id})
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.media(res.get('media'))
        return res
