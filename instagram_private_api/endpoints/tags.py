import json
from ..compat import compat_urllib_parse


class TagsEndpointsMixin(object):

    def tag_info(self, tag):
        """
        Get tag info

        :param tag:
        :return:
        """
        endpoint = 'tags/%(tag)s/info/' % {'tag': tag}
        res = self._call_api(endpoint)
        return res

    def tag_related(self, tag, **kwargs):
        """
        Get related tags

        :param tag:
        :return:
        """
        endpoint = 'tags/%(tag)s/related/' % {'tag': tag}
        params = {
            'visited': json.dumps([{'id': tag, 'type': 'hashtag'}], separators=(',', ':')),
            'related_types': json.dumps(['hashtag'], separators=(',', ':'))}
        if kwargs:
            params.update(kwargs)
        endpoint += '?' + compat_urllib_parse.urlencode(params)
        res = self._call_api(endpoint)
        return res

    def tag_search(self, text, **kwargs):
        """
        Search tag

        :param text:
        :param kwargs:
        :return:
        """
        endpoint = 'tags/search/'
        query = {
            'is_typeahead': True,
            'q': text,
            'rank_token': self.rank_token,
        }
        if kwargs:
            query.update(kwargs)
        endpoint += '?' + compat_urllib_parse.urlencode(query)
        res = self._call_api(endpoint)
        return res
