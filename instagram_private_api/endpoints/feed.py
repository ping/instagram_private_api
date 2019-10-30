import warnings

from .common import ClientDeprecationWarning
from ..compatpatch import ClientCompatPatch
from ..compat import compat_urllib_parse
from ..utils import raise_if_invalid_rank_token


class FeedEndpointsMixin(object):
    """For endpoints in ``/feed/``."""

    def feed_liked(self, **kwargs):
        """
        Get liked feed

        :param kwargs:
            - **max_id**: For pagination. Taken from ``next_max_id`` in the previous page.

        :return:
        """
        res = self._call_api('feed/liked/', query=kwargs)
        if self.auto_patch and res.get('items'):
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def feed_timeline(self, **kwargs):
        """
        Get timeline feed. To get a new timeline feed, you can mark a set of media
        as seen by setting seen_posts = comma-separated list of media IDs. Example:
        ``api.feed_timeline(seen_posts='123456789_12345,987654321_54321')``

        :param kwargs:
            - **max_id**: For pagination. Taken from ``next_max_id`` in the previous page.
        """
        params = {
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken,
            'is_prefetch': '0',
            'is_pull_to_refresh': '0',
            'phone_id': self.phone_id,
            'timezone_offset': self.timezone_offset,
        }
        params.update(kwargs)
        res = self._call_api('feed/timeline/', params=params, unsigned=True)
        if self.auto_patch:
            [ClientCompatPatch.media(m['media_or_ad'], drop_incompat_keys=self.drop_incompat_keys)
             if m.get('media_or_ad') else m
             for m in res.get('feed_items', [])]
        return res

    def feed_popular(self, **kwargs):   # pragma: no cover
        """Get popular feed. This endpoint is believed to be obsolete. Do not use."""
        warnings.warn(
            'This endpoint is believed to be obsolete. Do not use.',
            ClientDeprecationWarning)

        query = {
            'people_teaser_supported': '1',
            'rank_token': self.rank_token,
            'ranked_content': 'true'
        }
        query.update(kwargs)
        res = self._call_api('feed/popular/', query=query)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def user_feed(self, user_id, **kwargs):
        """
        Get the feed for the specified user id

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
            - **min_timestamp**: For pagination
        :return:
        """
        endpoint = 'feed/user/{user_id!s}/'.format(**{'user_id': user_id})
        res = self._call_api(endpoint, query=kwargs)

        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def self_feed(self, **kwargs):
        """Get authenticated user's own feed"""
        return self.user_feed(self.authenticated_user_id, **kwargs)

    def username_feed(self, user_name, **kwargs):
        """
        Get the feed for the specified user name

        :param user_name:
        :param kwargs:
            - **max_id**: For pagination
            - **min_timestamp**: For pagination
        :return:
        """
        endpoint = 'feed/user/{user_name!s}/username/'.format(**{'user_name': user_name})
        res = self._call_api(endpoint, query=kwargs)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def reels_tray(self, **kwargs):
        """Get story reels tray"""
        res = self._call_api('feed/reels_tray/', query=kwargs)
        if self.auto_patch:
            for u in res.get('tray', []):
                if not u.get('items'):
                    continue
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in u.get('items', [])]
        return res

    def user_reel_media(self, user_id, **kwargs):
        """
        Get user story/reel media

        :param user_id:
        :param kwargs:
        :return:
        """
        endpoint = 'feed/user/{user_id!s}/reel_media/'.format(**{'user_id': user_id})
        res = self._call_api(endpoint, query=kwargs)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def reels_media(self, user_ids, **kwargs):
        """
        Get multiple users' reel/story media

        :param user_ids: list of user IDs
        :param kwargs:
        :return:
        """
        user_ids = [str(x) for x in user_ids]
        params = {'user_ids': user_ids}
        params.update(kwargs)

        res = self._call_api('feed/reels_media/', params=params)
        if self.auto_patch:
            for reel_media in res.get('reels_media', []):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in reel_media.get('items', [])]
            for _, reel in list(res.get('reels', {}).items()):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in reel.get('items', [])]
        return res

    def feed_tag(self, tag, rank_token, **kwargs):
        """
        Get tag feed

        :param tag:
        :param rank_token: Required for paging through a single feed and can be generated with
            :meth:`generate_uuid`. You should use the same rank_token for paging through a single tag feed.
        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        raise_if_invalid_rank_token(rank_token)

        query_params = {
            'rank_token': rank_token
        }
        query_params.update(kwargs)
        endpoint = 'feed/tag/{tag!s}/'.format(
            **{'tag': compat_urllib_parse.quote(tag.encode('utf8'))})
        res = self._call_api(endpoint, query=query_params)
        if self.auto_patch:
            if res.get('items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('items', [])]
            if res.get('ranked_items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('ranked_items', [])]
            if res.get('story', {}).get('items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('story', {}).get('items', [])]
        return res

    def user_story_feed(self, user_id):
        """
        Get a user's story feed and current/replay broadcasts (if available)

        :param user_id:
        :return:
        """
        endpoint = 'feed/user/{user_id!s}/story/'.format(**{'user_id': user_id})
        res = self._call_api(endpoint)
        if self.auto_patch and res.get('reel'):
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('reel', {}).get('items', [])]
        return res

    def feed_location(self, location_id, rank_token, **kwargs):
        """
        This endpoint is believed to be obsolete. Do not use. Replaced by :meth:`location_section`.

        :param location_id:
        :param rank_token: Required for paging through a single feed and can be generated with
            :meth:`generate_uuid`. You should use the same rank_token for paging through a single location.
        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        warnings.warn(
            'This endpoint is believed to be obsolete. Do not use.',
            ClientDeprecationWarning)

        raise_if_invalid_rank_token(rank_token)

        endpoint = 'feed/location/{location_id!s}/'.format(**{'location_id': location_id})
        query_params = {
            'rank_token': rank_token,
        }
        query_params.update(kwargs)
        res = self._call_api(endpoint, query=query_params)
        if self.auto_patch:
            if res.get('items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('items', [])]
            if res.get('ranked_items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('ranked_items', [])]
            if res.get('story', {}).get('items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('story', {}).get('items', [])]
        return res

    def saved_feed(self, **kwargs):
        """
        Get saved photo feed

        :param kwargs:
            - **count**: Limit the number of items returned
        :return:
        """
        res = self._call_api('feed/saved/', query=kwargs)
        if self.auto_patch:
            [ClientCompatPatch.media(m['media'], drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', []) if m.get('media')]
        return res

    def feed_only_me(self, **kwargs):
        """
        Get feed of archived media

        :param kwargs
        """
        res = self._call_api('feed/only_me_feed/', query=kwargs)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res
