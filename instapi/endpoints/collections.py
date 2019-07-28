import json
from ..compatpatch import ClientCompatPatch


class CollectionsEndpointsMixin(object):
    """For endpoints in related to collections functionality."""

    def list_collections(self):
        return self._call_api('collections/list/')

    def collection_feed(self, collection_id, **kwargs):
        """
        Get the items in a collection.

        :param collection_id: Collection ID
        :return:
        """
        endpoint = 'feed/collection/{collection_id!s}/'.format(**{'collection_id': collection_id})
        res = self._call_api(endpoint, query=kwargs)
        if self.auto_patch and res.get('items'):
            [ClientCompatPatch.media(m['media'], drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', []) if m.get('media')]
        return res

    def create_collection(self, name, added_media_ids=None):
        """
        Create a new collection.

        :param name: Name for the collection
        :param added_media_ids: list of media_ids
        :return:
            .. code-block:: javascript

                {
                  "status": "ok",
                  "collection_id": "1700000000123",
                  "cover_media": {
                    "media_type": 1,
                    "original_width": 1080,
                    "original_height": 1080,
                    "id": 1492726080000000,
                    "image_versions2": {
                      "candidates": [
                        {
                          "url": "http://scontent-xx4-1.cdninstagram.com/...123.jpg",
                          "width": 1080,
                          "height": 1080
                        },
                        ...
                      ]
                    }
                  },
                  "collection_name": "A Collection"
                }
        """
        params = {'name': name}
        if added_media_ids and isinstance(added_media_ids, str):
            added_media_ids = [added_media_ids]
        if added_media_ids:
            params['added_media_ids'] = json.dumps(added_media_ids, separators=(',', ':'))
        params.update(self.authenticated_params)
        return self._call_api('collections/create/', params=params)

    def edit_collection(self, collection_id, added_media_ids):
        """
        Add media IDs to an existing collection.

        :param collection_id: Collection ID
        :param added_media_ids: list of media IDs
        :return: Returns same object as :meth:`create_collection`
        """
        if isinstance(added_media_ids, str):
            added_media_ids = [added_media_ids]
        params = {
            'added_media_ids': json.dumps(added_media_ids, separators=(',', ':'))
        }
        params.update(self.authenticated_params)
        endpoint = 'collections/{collection_id!s}/edit/'.format(**{'collection_id': collection_id})
        return self._call_api(endpoint, params=params)

    def delete_collection(self, collection_id):
        """
        Delete a collection.

        :param collection_id: Collection ID
        :return:
            .. code-block:: javascript

                {
                  "status": "ok"
                }
        """
        params = self.authenticated_params
        endpoint = 'collections/{collection_id!s}/delete/'.format(**{'collection_id': collection_id})
        return self._call_api(endpoint, params=params)
