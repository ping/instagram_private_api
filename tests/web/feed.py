
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
        results = self.api.tag_feed('catsofinstagram')
        self.assertIsNotNone(results.get('tag'))
        self.assertGreater(len(results.get('tag', {}).get('media', {}).get('nodes', [])), 0)
        self.assertGreater(len(results.get('tag', {}).get('top_posts', {}).get('nodes', [])), 0)

    def test_location_feed(self):
        results = self.api.location_feed('212988663')
        self.assertIsNotNone(results.get('location'))
        self.assertGreater(len(results.get('location', {}).get('media', {}).get('nodes', [])), 0)
        self.assertGreater(len(results.get('location', {}).get('top_posts', {}).get('nodes', [])), 0)
