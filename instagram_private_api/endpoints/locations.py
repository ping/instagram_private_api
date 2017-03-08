import json
import time
from ..compat import compat_urllib_parse


class LocationsEndpointsMixin(object):

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
        endpoint = 'locations/%(location_id)s/info/' % {'location_id': location_id}
        return self._call_api(endpoint)

    def location_related(self, location_id, **kwargs):
        """
        Get related locations

        :param location_id:
        :return:
        """
        endpoint = 'locations/%(location_id)s/related/' % {'location_id': location_id}
        params = {
            'visited': json.dumps([{'id': location_id, 'type': 'location'}], separators=(',', ':')),
            'related_types': json.dumps(['location'], separators=(',', ':'))}
        if kwargs:
            params.update(kwargs)
        endpoint += '?' + compat_urllib_parse.urlencode(params)
        return self._call_api(endpoint)

    def location_search(self, latitude, longitude, query=None):
        """
        Location search

        :param latitude:
        :param longitude:
        :param query:
        :return:
        """
        endpoint = 'location_search/'
        params = {
            'rank_token': self.rank_token,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': int(time.time())
        }
        if query:
            params['search_query'] = query
        endpoint += '?' + compat_urllib_parse.urlencode(params)
        return self._call_api(endpoint)
