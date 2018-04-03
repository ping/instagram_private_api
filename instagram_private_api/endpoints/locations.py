import json
import time

from ..utils import raise_if_invalid_rank_token


class LocationsEndpointsMixin(object):
    """For endpoints related to location functionality."""

    def location_info(self, location_id):
        """
        Get a location info

        :param location_id:
        :return:
            .. code-block:: javascript

                {
                  "status": "ok",
                  "location": {
                    "external_source": "facebook_places",
                    "city": "",
                    "name": "Berlin Brandenburger Tor",
                    "facebook_places_id": 114849465334163,
                    "address": "Pariser Platz",
                    "lat": 52.51588,
                    "pk": 229573811,
                    "lng": 13.37892
                  }
                }
        """
        endpoint = 'locations/{location_id!s}/info/'.format(**{'location_id': location_id})
        return self._call_api(endpoint)

    def location_related(self, location_id, **kwargs):
        """
        Get related locations

        :param location_id:
        :return:
        """
        endpoint = 'locations/{location_id!s}/related/'.format(**{'location_id': location_id})
        query = {
            'visited': json.dumps([{'id': location_id, 'type': 'location'}], separators=(',', ':')),
            'related_types': json.dumps(['location'], separators=(',', ':'))}
        query.update(kwargs)
        return self._call_api(endpoint, query=query)

    def location_search(self, latitude, longitude, query=None, **kwargs):
        """
        Location search

        :param latitude:
        :param longitude:
        :param query:
        :return:
        """
        query_params = {
            'rank_token': self.rank_token,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': int(time.time())
        }
        if query:
            query_params['search_query'] = query
        query_params.update(kwargs)
        return self._call_api('location_search/', query=query_params)

    def location_fb_search(self, query, rank_token, exclude_list=[], **kwargs):
        """
        Search for locations by query text

        :param query: search terms
        :param rank_token: Required for paging through a single feed. See examples/pagination.py
        :param exclude_list: List of numerical location IDs to exclude
        :param kwargs:
        :return:
        """
        raise_if_invalid_rank_token(rank_token)

        if not exclude_list:
            exclude_list = []

        query_params = {
            'query': query,
            'timezone_offset': self.timezone_offset,
            'count': 30,
            'exclude_list': json.dumps(exclude_list, separators=(',', ':')),
            'rank_token': rank_token,
        }
        query_params.update(kwargs)
        return self._call_api('fbsearch/places/', query=query_params)
