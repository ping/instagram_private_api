import unittest
import json

from ..common import (
    ApiTestBase, compat_mock
)


class CollectionsTests(ApiTestBase):
    """Tests for CollectionsEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_create_collection',
                'test': CollectionsTests('test_create_collection', api)
            },
            {
                'name': 'test_create_collection_mock',
                'test': CollectionsTests('test_create_collection_mock', api)
            },
            {
                'name': 'test_collection_feed',
                'test': CollectionsTests('test_collection_feed', api)
            },
            {
                'name': 'test_edit_collection',
                'test': CollectionsTests('test_edit_collection', api)
            },
            {
                'name': 'test_edit_collection_mock',
                'test': CollectionsTests('test_edit_collection_mock', api)
            },
            {
                'name': 'test_delete_collection',
                'test': CollectionsTests('test_delete_collection', api)
            },
            {
                'name': 'test_delete_collection_mock',
                'test': CollectionsTests('test_delete_collection_mock', api)
            },
        ]

    def test_collection_feed(self):
        results = self.api.list_collections()
        self.assertTrue(results.get('items'), 'No collection')

        first_collection_id = results['items'][0]['collection_id']
        results = self.api.collection_feed(first_collection_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(str(results.get('collection_id', '')), first_collection_id)
        self.assertIsNotNone(results.get('items'))

    @unittest.skip('Modifies data.')
    def test_create_collection(self):
        name = 'A Collection'
        results = self.api.create_collection(name)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('collection_id'))
        self.assertEqual(results.get('collection_name'), name)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_create_collection_mock(self, call_api):
        name = 'A Collection'
        call_api.return_value = {
            'status': 'ok',
            'collection_id': 123, 'collection_name': name}

        media_ids = ['1495028858729943288_25025320']
        params = {'name': name, 'added_media_ids': json.dumps(media_ids, separators=(',', ':'))}
        params.update(self.api.authenticated_params)
        self.api.create_collection(name, media_ids)
        call_api.assert_called_with(
            'collections/create/',
            params=params)
        self.api.create_collection(name, media_ids[0])
        call_api.assert_called_with(
            'collections/create/',
            params=params)

    @unittest.skip('Modifies data.')
    def test_edit_collection(self):
        results = self.api.list_collections()
        self.assertTrue(results.get('items'), 'No collections')

        first_collection_id = results['items'][0]['collection_id']
        results = self.api.edit_collection(first_collection_id, ['1495028858729943288_25025320'])
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('collection_id'))

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_edit_collection_mock(self, call_api):
        collection_id = 123
        call_api.return_value = {
            'status': 'ok',
            'collection_id': collection_id, 'collection_name': 'A Collection'}

        media_ids = ['1495028858729943288_25025320']
        params = {'added_media_ids': json.dumps(media_ids, separators=(',', ':'))}
        params.update(self.api.authenticated_params)

        self.api.edit_collection(collection_id, media_ids)
        call_api.assert_called_with(
            'collections/{collection_id!s}/edit/'.format(**{'collection_id': collection_id}),
            params=params)
        self.api.edit_collection(collection_id, media_ids[0])
        call_api.assert_called_with(
            'collections/{collection_id!s}/edit/'.format(**{'collection_id': collection_id}),
            params=params)

    @unittest.skip('Modifies data.')
    def test_delete_collection(self):
        results = self.api.list_collections()
        self.assertTrue(results.get('items'), 'No collections')

        first_collection_id = results['items'][0]['collection_id']
        results = self.api.delete_collection(first_collection_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_delete_collection_mock(self, call_api):
        collection_id = 123
        call_api.return_value = {'status': 'ok'}

        self.api.delete_collection(collection_id)
        call_api.assert_called_with(
            'collections/{collection_id!s}/delete/'.format(**{'collection_id': collection_id}),
            params=self.api.authenticated_params)
