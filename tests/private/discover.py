import unittest

from ..common import ApiTestBase


class DiscoverTests(ApiTestBase):
    """Tests for DiscoverEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_discover_channels_home',
                'test': DiscoverTests('test_discover_channels_home', api)
            },
            {
                'name': 'test_discover_chaining',
                'test': DiscoverTests('test_discover_chaining', api, user_id='329452045')
            },
            {
                'name': 'test_explore',
                'test': DiscoverTests('test_explore', api)
            },
            {
                'name': 'test_discover_top_live',
                'test': DiscoverTests('test_discover_top_live', api)
            },
            {
                'name': 'test_top_live_status',
                'test': DiscoverTests('test_top_live_status', api)
            },
        ]

    def test_explore(self):
        results = self.api.explore()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    @unittest.skip('Deprecated.')
    def test_discover_channels_home(self):
        results = self.api.discover_channels_home()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_discover_chaining(self):
        results = self.api.discover_chaining(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No users returned.')

    def test_discover_top_live(self):
        results = self.api.discover_top_live()
        self.assertEqual(results.get('status'), 'ok')
        self.assertTrue('broadcasts' in results)

    def test_top_live_status(self):
        results = self.api.discover_top_live()
        broadcast_ids = [b['id'] for b in results.get('broadcasts', [])]
        if broadcast_ids:
            results = self.api.top_live_status(broadcast_ids)
            self.assertEqual(results.get('status'), 'ok')
            self.assertGreater(len(results.get('broadcast_status_items', [])), 0, 'No broadcast_status_items returned.')

            results = self.api.top_live_status(str(broadcast_ids[0]))
            self.assertEqual(results.get('status'), 'ok')
            self.assertGreater(len(results.get('broadcast_status_items', [])), 0, 'No broadcast_status_items returned.')
