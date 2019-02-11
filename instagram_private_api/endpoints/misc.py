import warnings

from .common import ClientDeprecationWarning
from ..constants import Constants
from ..compatpatch import ClientCompatPatch


class MiscEndpointsMixin(object):
    """For miscellaneous functions."""

    def sync(self, prelogin=False):
        """Synchronise experiments."""
        if prelogin:
            params = {
                'id': self.generate_uuid(),
                'experiments': Constants.LOGIN_EXPERIMENTS
            }
        else:
            params = {
                'id': self.authenticated_user_id,
                'experiments': Constants.EXPERIMENTS
            }
            params.update(self.authenticated_params)
        return self._call_api('qe/sync/', params=params)

    def expose(self, experiment='ig_android_profile_contextual_feed'):  # pragma: no cover
        warnings.warn(
            'This endpoint is believed to be obsolete. Do not use.',
            ClientDeprecationWarning)

        params = {
            'id': self.authenticated_user_id,
            'experiment': experiment
        }
        params.update(self.authenticated_params)
        return self._call_api('qe/expose/', params=params)

    def megaphone_log(self, log_type='feed_aysf', action='seen', reason='', **kwargs):
        """
        A tracking endpoint of sorts

        :param log_type:
        :param action:
        :param reason:
        :param kwargs:
        :return:
        """
        params = {
            'type': log_type,
            'action': action,
            'reason': reason,
            '_uuid': self.uuid,
            'device_id': self.device_id,
            '_csrftoken': self.csrftoken,
            'uuid': self.generate_uuid(return_hex=True)
        }
        params.update(kwargs)
        return self._call_api('megaphone/log/', params=params, unsigned=True)

    def ranked_recipients(self):
        """Get ranked recipients"""
        res = self._call_api('direct_v2/ranked_recipients/', query={'show_threads': 'true'})
        return res

    def recent_recipients(self):
        """Get recent recipients"""
        res = self._call_api('direct_share/recent_recipients/')
        return res

    def news(self, **kwargs):
        """
        Get news feed of accounts the logged in account is following.
        This returns the items in the 'Following' tab.
        """
        return self._call_api('news/', query=kwargs)

    def news_inbox(self):
        """
        Get inbox feed of activity related to the logged in account.
        This returns the items in the 'You' tab.
        """
        return self._call_api(
            'news/inbox/', query={'limited_activity': 'true', 'show_su': 'true'})

    def direct_v2_inbox(self):
        """Get v2 inbox"""
        return self._call_api('direct_v2/inbox/')

    def oembed(self, url, **kwargs):
        """
        Get oembed info

        :param url:
        :param kwargs:
        :return:
        """
        query = {'url': url}
        query.update(kwargs)
        res = self._call_api('oembed/', query=query)
        return res

    def translate(self, object_id, object_type):
        """

        :param object_id: id value for the object
        :param object_type: One of [1, 2, 3] where
                            1 = CAPTION - unsupported
                            2 = COMMENT - unsupported
                            3 = BIOGRAPHY
        :return:
        """
        warnings.warn('This endpoint is not tested fully.', UserWarning)
        res = self._call_api(
            'language/translate/',
            query={'id': object_id, 'type': object_type})
        return res

    def bulk_translate(self, comment_ids):
        """
        Get translations of comments

        :param comment_ids: list of comment/caption IDs
        :return:
        """
        if isinstance(comment_ids, str):
            comment_ids = [comment_ids]
        query = {'comment_ids': ','.join(comment_ids)}
        res = self._call_api('language/bulk_translate/', query=query)
        return res

    def top_search(self, query):
        """
        Search for top matching hashtags, users, locations

        :param query: search terms
        :return:
        """
        res = self._call_api(
            'fbsearch/topsearch/',
            query={'context': 'blended', 'ranked_token': self.rank_token, 'query': query})
        if self.auto_patch and res.get('users', []):
            [ClientCompatPatch.list_user(u['user']) for u in res['users']]
        return res

    def stickers(self, sticker_type='static_stickers', location=None):
        """
        Get sticker assets

        :param sticker_type: One of ['static_stickers']
        :param location: dict containing 'lat', 'lng', 'horizontalAccuracy'.
                         Example: {'lat': '', 'lng': '', 'horizontalAccuracy': ''}
                         'horizontalAccuracy' is a float in meters representing the estimated horizontal accuracy
                         https://developer.android.com/reference/android/location/Location.html#getAccuracy()
        :return:
        """
        if sticker_type not in ['static_stickers']:
            raise ValueError('Invalid sticker_type: {0!s}'.format(sticker_type))
        if location and not ('lat' in location and 'lng' in location and 'horizontalAccuracy' in location):
            raise ValueError('Invalid location')
        params = {
            'type': sticker_type
        }
        if location:
            params['lat'] = location['lat']
            params['lng'] = location['lng']
            params['horizontalAccuracy'] = location['horizontalAccuracy']
        params.update(self.authenticated_params)
        return self._call_api('creatives/assets/', params=params)
