import json

from ..compat import compat_urllib_parse
from ..utils import raise_if_invalid_rank_token
from ..compatpatch import ClientCompatPatch


class TagsEndpointsMixin(object):
    """For endpoints in ``/tags/``."""

    def tag_info(self, tag):
        """
        Get tag info

        :param tag:
        :return:
        """
        endpoint = 'tags/{tag!s}/info/'.format(
            **{'tag': compat_urllib_parse.quote(tag.encode('utf8'))})
        res = self._call_api(endpoint)
        return res

    def tag_related(self, tag, **kwargs):
        """
        Get related tags

        :param tag:
        :return:
        """
        endpoint = 'tags/{tag!s}/related/'.format(
            **{'tag': compat_urllib_parse.quote(tag.encode('utf8'))})
        query = {
            'visited': json.dumps([{'id': tag, 'type': 'hashtag'}], separators=(',', ':')),
            'related_types': json.dumps(['hashtag', 'location'], separators=(',', ':'))}
        res = self._call_api(endpoint, query=query)
        return res

    def tag_search(self, text, rank_token, exclude_list=[], **kwargs):
        """
        Search tag

        :param text: Search term
        :param rank_token: Required for paging through a single feed. See examples/pagination.py
        :param exclude_list: List of numerical tag IDs to exclude
        :param kwargs:
        :return:
        """
        raise_if_invalid_rank_token(rank_token)
        if not exclude_list:
            exclude_list = []
        query = {
            'q': text,
            'timezone_offset': self.timezone_offset,
            'count': 30,
            'exclude_list': json.dumps(exclude_list, separators=(',', ':')),
            'rank_token': rank_token,
        }
        query.update(kwargs)
        res = self._call_api('tags/search/', query=query)
        return res

    def tags_user_following(self, user_id):
        """
        Get tags a user is following

        :param user_id:
        :return:
        """
        endpoint = 'users/{user_id!s}/following_tags_info/'.format(user_id=user_id)
        return self._call_api(endpoint)

    def tag_follow_suggestions(self):
        """Get suggestions for tags to follow"""
        return self._call_api('tags/suggested/')

    def tag_follow(self, tag):
        """
        Follow a tag

        :param tag:
        :return:
        """
        endpoint = 'tags/follow/{hashtag!s}/'.format(
            hashtag=compat_urllib_parse.quote(tag.encode('utf-8')))
        return self._call_api(endpoint, params=self.authenticated_params)

    def tag_unfollow(self, tag):
        """
        Unfollow a tag

        :param tag:
        :return:
        """
        endpoint = 'tags/unfollow/{hashtag!s}/'.format(
            hashtag=compat_urllib_parse.quote(tag.encode('utf-8')))
        return self._call_api(endpoint, params=self.authenticated_params)

    def tag_section(self, tag, tab='top', **kwargs):
        """
        Get a tag feed section

        :param tag: tag text (without '#')
        :param tab: One of 'top', 'recent', 'places'
        :kwargs:
            **extract**: return the array of media items only
            **page**: for pagination
            **next_media_ids**: array of media_id (int) for pagination
            **max_id**: for pagination
        :return:
        """
        valid_tabs = ['top', 'recent', 'places']
        if tab not in valid_tabs:
            raise ValueError('Invalid tab: {}'.format(tab))

        extract_media_only = kwargs.pop('extract', False)
        endpoint = 'tags/{tag!s}/sections/'.format(
            **{'tag': compat_urllib_parse.quote(tag.encode('utf8'))})

        params = {
            'supported_tabs': json.dumps(valid_tabs, separators=(',', ':')),
            'tab': tab,
            'include_persistent': True,
        }

        # explicitly set known paging parameters to avoid triggering server-side errors
        if kwargs.get('max_id'):
            params['max_id'] = kwargs.pop('max_id')
        if kwargs.get('page'):
            params['page'] = kwargs.pop('page')
        if kwargs.get('next_media_ids'):
            params['next_media_ids'] = json.dumps(kwargs.pop('next_media_ids'), separators=(',', ':'))
        kwargs.pop('max_id', None)
        kwargs.pop('page', None)
        kwargs.pop('next_media_ids', None)

        params.update(kwargs)
        results = self._call_api(endpoint, params=params, unsigned=True)
        extracted_medias = []
        if self.auto_patch:
            for s in results.get('sections', []):
                for m in s.get('layout_content', {}).get('medias', []):
                    if m.get('media'):
                        ClientCompatPatch.media(m['media'], drop_incompat_keys=self.drop_incompat_keys)
                        if extract_media_only:
                            extracted_medias.append(m['media'])
        if extract_media_only:
            return extracted_medias
        return results
