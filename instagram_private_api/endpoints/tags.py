import json


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
        query = {
            'visited': json.dumps([{'id': tag, 'type': 'hashtag'}], separators=(',', ':')),
            'related_types': json.dumps(['hashtag'], separators=(',', ':'))}
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
            'is_typeahead': True,
            'q': text,
            'rank_token': self.rank_token,
        }
        if kwargs:
            query.update(kwargs)
        res = self._call_api('tags/search/', query=query)
        return res
