import json
import time

from ..utils import raise_if_invalid_rank_token
from ..compatpatch import ClientCompatPatch


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

    def location_section(self, location_id, rank_token, tab='ranked', **kwargs):
        """
        Get a location feed

        :param location_id:
        :param rank_token: Required for paging through a single feed and can be generated with
            :meth:`generate_uuid`. You should use the same rank_token for paging through a single location.
        :param tab: One of 'ranked', 'recent'
        :kwargs:
            **extract**: return the array of media items only
            **page**: for pagination
            **next_media_ids**: array of media_id (int) for pagination
            **max_id**: for pagination
        :return:
        """
        raise_if_invalid_rank_token(rank_token)
        if tab not in ('ranked', 'recent'):
            raise ValueError('Invalid tab: {}'.format(tab))

        extract_media_only = kwargs.pop('extract', False)
        endpoint = 'locations/{location_id!s}/sections/'.format(**{'location_id': location_id})
        params = {
            'rank_token': rank_token,
            'tab': tab,
            'session_id': self.session_id,
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

    def location_stories(self, location_id, **kwargs):
        """
        Get a location story feed

        :param location_id:
        :param rank_token: Required for paging through a single feed and can be generated with
            :meth:`generate_uuid`. You should use the same rank_token for paging through a single location.
        :return:
        """
        endpoint = 'locations/{location_id!s}/story/'.format(**{'location_id': location_id})
        # params = {
        #     'rank_token': rank_token,
        #     'tab': tab,
        #     'session_id': self.session_id,
        # }
        # params.update(kwargs)
        # return self._call_api(endpoint, params=params)
        return self._call_api(endpoint)
