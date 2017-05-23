import json
import time


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

    def location_fb_search(self, query):
        """
        Search for locations by query text

        :param query: search terms
        :return:
        """
        return self._call_api(
            'fbsearch/places/',
            query={'ranked_token': self.rank_token, 'query': query})
