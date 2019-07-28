import re

from ..compatpatch import ClientCompatPatch

USER_CHANNEL_ID_RE = r'^user_[1-9]\d+$'


class IGTVEndpointsMixin(object):
    """For endpoints in ``/igtv/``."""

    def tvchannel(self, channel_id, **kwargs):
        """
        Get channel

        :param channel_id: One of 'for_you', 'chrono_following', 'popular', 'continue_watching'
            (as returned by :meth:`tvguide`) or for a user 'user_12345' where user_id = '12345'
        """
        if (channel_id not in ('for_you', 'chrono_following', 'popular', 'continue_watching')
                and not re.match(USER_CHANNEL_ID_RE, channel_id)):
            raise ValueError('Invalid channel_id: {}'.format(channel_id))

        endpoint = 'igtv/channel/'
        params = {'id': channel_id}
        params.update(self.authenticated_params)
        if kwargs:
            params.update(kwargs)
        res = self._call_api(endpoint, params=params)

        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]

        return res

    def tvguide(self):
        """TV guide to popular, following, suggested channels, etc"""
        res = self._call_api('igtv/tv_guide/')
        if self.auto_patch:
            for c in res.get('channels', []):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in c.get('items', [])]
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('my_channel', {}).get('items', [])]
        return res

    def search_igtv(self, text):
        """
        Search igtv

        :param text: Search term
        """
        text = text.strip()
        if not text.strip():
            raise ValueError('Search text cannot be empty')

        res = self._call_api('igtv/search/', query={'query': text})
        if self.auto_patch:
            for r in res.get('results', []):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in r.get('channel', {}).get('items', [])]
                if r.get('user'):
                    ClientCompatPatch.user(r['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res
