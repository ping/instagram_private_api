import warnings
from ..compat import compat_urllib_parse
from ..constants import Constants
from ..compatpatch import ClientCompatPatch


class MiscEndpointsMixin(object):

    def sync(self, prelogin=False):
        """Synchronise experiments."""
        endpoint = 'qe/sync/'
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
        return self._call_api(endpoint, params=params)

    def expose(self, experiment='ig_android_profile_contextual_feed'):
        endpoint = 'qe/expose/'
        params = {
            'id': self.authenticated_user_id,
            'experiment': experiment
        }
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def megaphone_log(self, log_type='feed_aysf', action='seen', reason='', **kwargs):
        """
        A tracking endpoint of sorts

        :param log_type:
        :param action:
        :param reason:
        :param kwargs:
        :return:
        """
        endpoint = 'megaphone/log/'
        params = {
            'type': log_type,
            'action': action,
            'reason': reason,
            '_uuid': self.uuid,
            'device_id': self.device_id,
            '_csrftoken': self.csrftoken,
            'uuid': self.generate_uuid(return_hex=True)
        }
        if kwargs:
            params.update(kwargs)
        return self._call_api(endpoint, params=params, unsigned=True)

    def ranked_recipients(self):
        """Get ranked recipients"""
        res = self._call_api('direct_v2/ranked_recipients/?' + compat_urllib_parse.urlencode(
            {'show_threads': 'true'}))
        return res

    def recent_recipients(self):
        """Get recent recipients"""
        res = self._call_api('direct_share/recent_recipients/')
        return res

    def news(self):
        """Get news"""
        return self._call_api('news/')

    def news_inbox(self):
        """Get news inbox"""
        return self._call_api('news/inbox/?' + compat_urllib_parse.urlencode(
            {'limited_activity': 'true', 'show_su': 'true'}))

    def direct_v2_inbox(self):
        """Get v2 inbox"""
        return self._call_api('direct_v2/inbox/')

    def oembed(self, url, **kwargs):
        """Get oembed info"""
        endpoint = 'oembed?'
        params = {'url': url}
        if kwargs:
            params.update(kwargs)
        endpoint += compat_urllib_parse.urlencode(params)
        res = self._call_api(endpoint)
        return res

    def translate(self, object_id, object_type):
        warnings.warn('This endpoint is not tested fully.', UserWarning)
        """type values:
            - 1 = CAPTION - unsupported
            - 2 = COMMENT - unsupported
            - 3 = BIOGRAPHY
        """
        endpoint = 'language/translate/' + '?' + compat_urllib_parse.urlencode({
            'id': object_id, 'type': object_type})
        res = self._call_api(endpoint)
        return res

    def bulk_translate(self, comment_ids):
        """
        Get translations of comments

        :param comment_ids: list of comment/caption IDs
        :return:
        """
        if isinstance(comment_ids, str):
            comment_ids = [comment_ids]

        endpoint = 'language/bulk_translate/'
        params = {'comment_ids': ','.join(comment_ids)}
        endpoint += '?' + compat_urllib_parse.urlencode(params)
        res = self._call_api(endpoint)
        return res

    def location_fb_search(self, query):
        """
        Search for locations by query text

        :param query: search terms
        :return:
        """
        endpoint = 'fbsearch/places/?' + compat_urllib_parse.urlencode(
            {'ranked_token': self.rank_token, 'query': query})
        res = self._call_api(endpoint)
        return res

    def top_search(self, query):
        """
        Search for top matching hashtags, users, locations

        :param query: search terms
        :return:
        """
        endpoint = 'fbsearch/topsearch/?' + compat_urllib_parse.urlencode({
            'context': 'blended', 'ranked_token': self.rank_token, 'query': query})
        res = self._call_api(endpoint)
        if self.auto_patch and res.get('users', []):
            [ClientCompatPatch.list_user(u['user']) for u in res['users']]
        return res

    def stickers(self, sticker_type='static_stickers', location=None):
        """
        Get sticker assets

        :param sticker_type: One of ['static_stickers']
        :param location: dict containing 'lat', 'lng', 'horizontalAccuracy'.
            Example: {'lat': '', 'lng': '', 'horizontalAccuracy': ''}
        :return:
        """
        if sticker_type not in ['static_stickers']:
            raise ValueError('Invalid sticker_type: %s' % sticker_type)
        if location and not ('lat' in location and 'lng' in location and 'horizontalAccuracy' in location):
            raise ValueError('Invalid location')
        endpoint = 'creatives/assets/'
        params = {
            'type': sticker_type
        }
        if location:
            params['lat'] = location['lat']
            params['lng'] = location['lng']
            params['horizontalAccuracy'] = location['horizontalAccuracy']
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)
