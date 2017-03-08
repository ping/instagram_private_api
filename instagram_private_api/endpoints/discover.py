from ..compat import compat_urllib_parse
from ..compatpatch import ClientCompatPatch


class DiscoverEndpointsMixin(object):

    def explore(self, **kwargs):
        """Get explore items"""
        query = {'is_prefetch': 'false', 'is_from_promote': 'false'}
        if kwargs:
            query.update(kwargs)
        res = self._call_api('discover/explore/?' + compat_urllib_parse.urlencode(query))
        if self.auto_patch:
            [ClientCompatPatch.media(item['media'], drop_incompat_keys=self.drop_incompat_keys)
             if item.get('media') else item for item in res['items']]
        return res

    def discover_channels_home(self):
        """Discover channels home"""
        endpoint = 'discover/channels_home/'
        res = self._call_api(endpoint)
        if self.auto_patch:
            for item in res.get('items', []):
                for row_item in item.get('row_items', []):
                    if row_item.get('media'):
                        ClientCompatPatch.media(row_item['media'])
        return res

    def discover_chaining(self, user_id):
        """
        Get suggested users

        :param user_id:
        :return:
        """
        endpoint = 'discover/chaining/?' + compat_urllib_parse.urlencode(
            {'target_id': user_id})
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(user) for user in res.get('users', [])]
        return res

    def discover_top_live(self, **kwargs):
        """
        Get top live broadcasts

        :param kwargs:
            - max_id: For pagination
        :return:
        """
        endpoint = 'discover/top_live/'
        if kwargs:
            endpoint += '?' + compat_urllib_parse.urlencode(kwargs)
        return self._call_api(endpoint)

    def top_live_status(self, broadcast_ids):
        """
        Get status for a list of broadcast_ids

        :return:
        """
        if isinstance(broadcast_ids, str):
            broadcast_ids = [broadcast_ids]
        broadcast_ids = list(map(lambda x: str(x), broadcast_ids))
        params = {'broadcast_ids': broadcast_ids}
        params.update(self.authenticated_params)
        endpoint = 'discover/top_live_status/'
        return self._call_api(endpoint, params=params)
