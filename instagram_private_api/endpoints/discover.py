import warnings

from .common import ClientDeprecationWarning
from ..compatpatch import ClientCompatPatch


class DiscoverEndpointsMixin(object):
    """For endpoints in ``/discover/``."""

    def explore(self, **kwargs):
        """
        Get explore items

        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        query = {'is_prefetch': 'false', 'is_from_promote': 'false'}
        query.update(kwargs)
        res = self._call_api('discover/explore/', query=query)
        if self.auto_patch:
            [ClientCompatPatch.media(item['media'], drop_incompat_keys=self.drop_incompat_keys)
             if item.get('media') else item for item in res['items']]
        return res

    def discover_channels_home(self):       # pragma: no cover
        """Discover channels home"""
        warnings.warn(
            'This endpoint is believed to be obsolete. Do not use.',
            ClientDeprecationWarning)

        res = self._call_api('discover/channels_home/')
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
        res = self._call_api('discover/chaining/', query={'target_id': user_id})
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
        return self._call_api('discover/top_live/', query=kwargs)

    def top_live_status(self, broadcast_ids):
        """
        Get status for a list of broadcast_ids

        :return:
        """
        if isinstance(broadcast_ids, str):
            broadcast_ids = [broadcast_ids]
        broadcast_ids = [str(x) for x in broadcast_ids]
        params = {'broadcast_ids': broadcast_ids}
        params.update(self.authenticated_params)
        return self._call_api('discover/top_live_status/', params=params)
