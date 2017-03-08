from ..compat import compat_urllib_parse
from ..compatpatch import ClientCompatPatch


class UsertagsEndpointsMixin(object):

    def usertag_feed(self, user_id, **kwargs):
        """
        Get a usertag feed

        :param user_id:
        :param kwargs:
        :return:
        """
        endpoint = 'usertags/%(user_id)s/feed/' % {'user_id': user_id}
        query = {'rank_token': self.rank_token, 'ranked_content': 'true'}
        if kwargs:
            query.update(kwargs)
        endpoint += '?' + compat_urllib_parse.urlencode(query)
        res = self._call_api(endpoint)
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
        endpoint = 'usertags/%(media_id)s/remove/' % {'media_id': media_id}
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.media(res.get('media'))
        return res
