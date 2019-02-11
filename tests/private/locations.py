
from ..common import ApiTestBase


class LocationTests(ApiTestBase):
    """Tests for LocationsEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_location_info',
                'test': LocationTests('test_location_info', api)
            },
            {
                'name': 'test_location_related',
                'test': LocationTests('test_location_related', api)
            },
            {
                'name': 'test_location_search',
                'test': LocationTests('test_location_search', api)
            },
            {
                'name': 'test_location_fb_search',
                'test': LocationTests('test_location_fb_search', api)
            },
            {
                'name': 'test_location_section',
                'test': LocationTests('test_location_section', api)
            },
        ]

    def test_location_info(self):
        results = self.api.location_info(229573811)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('location'))

    def test_location_related(self):
        results = self.api.location_related(229573811)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('related'))

    def test_location_search(self):
        results = self.api.location_search('40.7484445', '-73.9878531', query='Empire')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('venues', [])), 0, 'No venues returned.')

    def test_location_fb_search(self):
        rank_token = self.api.generate_uuid()
        results = self.api.location_fb_search('Paris, France', rank_token)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_location_section(self):
        results = self.api.location_section(229573811, self.api.generate_uuid())
        self.assertEqual(results.get('status'), 'ok')
        self.assertIn('sections', results)
        self.assertGreater(len(results.get('sections', [])), 0, 'No results returned.')
