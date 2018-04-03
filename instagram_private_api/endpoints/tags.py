import json

from ..compat import compat_urllib_parse
from ..utils import raise_if_invalid_rank_token


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
