
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
            {
                'name': 'test_timeline_feed',
                'test': FeedTests('test_timeline_feed', api),
            },
            {
                'name': 'test_reels_tray',
                'test': FeedTests('test_reels_tray', api),
            },
            {
                'name': 'test_reels_feed',
                'test': FeedTests('test_reels_feed', api),
            },
            {
                'name': 'test_highlight_reels',
                'test': FeedTests('test_highlight_reels', api),
            },
            {
                'name': 'test_tagged_user_feed',
                'test': FeedTests('test_tagged_user_feed', api),
            },
            {
                'name': 'test_tag_story_feed',
                'test': FeedTests('test_tag_story_feed', api),
            },
            {
                'name': 'test_location_story_feed',
                'test': FeedTests('test_location_story_feed', api),
            }
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

    def test_timeline_feed(self):
        results = self.api.timeline_feed().get('data', {})
        self.assertIsNotNone(results.get('user', {}).get('username'))
        self.assertGreater(
            len(results.get('user', {}).get('edge_web_feed_timeline', {}).get('edges', [])), 0)

    def test_reels_tray(self):
        results = self.api.reels_tray().get('data', {})
        self.assertGreater(
            len(results.get('user', {}).get(
                'feed_reels_tray', {}).get(
                    'edge_reels_tray_to_reel', {}).get('edges', [])), 0)

    def test_reels_feed(self):
        results = self.api.reels_feed(['25025320']).get('data', {})
        self.assertTrue('reels_media' in results)

    def test_highlight_reels(self):
        results = self.api.highlight_reels('25025320').get('data', {}).get('user', {})
        self.assertTrue('edge_highlight_reels' in results)

    def test_tagged_user_feed(self):
        results = self.api.tagged_user_feed('25025320').get('data', {}).get('user', {})
        self.assertTrue('edge_user_to_photos_of_you' in results)

    def test_tag_story_feed(self):
        results = self.api.tag_story_feed('catsofinstagram').get('data', {})
        self.assertTrue('reels_media' in results)

    def test_location_story_feed(self):
        results = self.api.location_story_feed('7226110').get('data', {})
        self.assertTrue('reels_media' in results)
