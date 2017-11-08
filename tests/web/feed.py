
from ..common import WebApiTestBase


class FeedTests(WebApiTestBase):
    """Tests for media related functions."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_tag_feed',
                'test': FeedTests('test_tag_feed', api),
            },
            {
                'name': 'test_location_feed',
                'test': FeedTests('test_location_feed', api),
            },
        ]

    def test_tag_feed(self):
        results = self.api.tag_feed('catsofinstagram').get('data', {})
        self.assertIsNotNone(results.get('hashtag', {}).get('name'))
        self.assertGreater(
            len(results.get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])), 0)
        self.assertGreater(
            len(results.get('hashtag', {}).get('edge_hashtag_to_top_posts', {}).get('edges', [])), 0)

    def test_location_feed(self):
        results = self.api.location_feed('212988663').get('data', {})
        self.assertIsNotNone(results.get('location', {}).get('name'))
        self.assertGreater(
            len(results.get('location', {}).get('edge_location_to_media', {}).get('edges', [])), 0)
        self.assertGreater(
            len(results.get('location', {}).get('edge_location_to_top_posts', {}).get('edges', [])), 0)
