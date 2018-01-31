import json

from ..compat import compat_urllib_parse


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

    def tag_search(self, text, **kwargs):
        """
        Search tag

        :param text:
        :param kwargs:
        :return:
        """
        query = {
            'q': text,
            'timezone_offset': self.timezone_offset,
            'count': 30,
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
