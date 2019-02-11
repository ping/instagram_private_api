
from ..common import WebApiTestBase


class UnauthenticatedTests(WebApiTestBase):
    """Tests for endpoints with authentication"""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_unauthenticated_tag_feed',
                'test': UnauthenticatedTests('test_unauthenticated_tag_feed', api),
            },
            {
                'name': 'test_unauthenticated_user_feed',
                'test': UnauthenticatedTests('test_unauthenticated_user_feed', api),
            },
            {
                'name': 'test_unauthenticated_location_feed',
                'test': UnauthenticatedTests('test_unauthenticated_location_feed', api),
            },
            {
                'name': 'test_unauthenticated_media_comments',
                'test': UnauthenticatedTests('test_unauthenticated_media_comments', api),
            },
            {
                'name': 'test_unauthenticated_media_comments_noextract',
                'test': UnauthenticatedTests('test_unauthenticated_media_comments_noextract', api),
            },
            {
                'name': 'test_unauthenticated_user_info2',
                'test': UnauthenticatedTests('test_unauthenticated_user_info2', api),
            },
            {
                'name': 'test_unauthenticated_tag_story_feed',
                'test': UnauthenticatedTests('test_unauthenticated_tag_story_feed', api),
            },
            {
                'name': 'test_unauthenticated_location_story_feed',
                'test': UnauthenticatedTests('test_unauthenticated_location_story_feed', api),
            },
        ]

    def test_unauthenticated_tag_feed(self):
        results = self.api.tag_feed('catsofinstagram').get('data', {})
        self.assertIsNotNone(results.get('hashtag', {}).get('name'))
        self.assertGreater(
            len(results.get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])), 0)
        self.assertGreater(
            len(results.get('hashtag', {}).get('edge_hashtag_to_top_posts', {}).get('edges', [])), 0)

    def test_unauthenticated_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_unauthenticated_location_feed(self):
        results = self.api.location_feed('212988663').get('data', {})
        self.assertIsNotNone(results.get('location', {}).get('name'))
        self.assertGreater(
            len(results.get('location', {}).get('edge_location_to_media', {}).get('edges', [])), 0)
        self.assertGreater(
            len(results.get('location', {}).get('edge_location_to_top_posts', {}).get('edges', [])), 0)

    def test_unauthenticated_media_comments(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20)
        self.assertGreaterEqual(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_unauthenticated_media_comments_noextract(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20, extract=False)
        self.assertIsInstance(results, dict)

    def test_unauthenticated_user_info2(self):
        results = self.api.user_info2('instagram')
        self.assertIsNotNone(results.get('id'))

    def test_unauthenticated_tag_story_feed(self):
        results = self.api.tag_story_feed('catsofinstagram').get('data', {})
        self.assertTrue('reels_media' in results)

    def test_unauthenticated_location_story_feed(self):
        results = self.api.location_story_feed('7226110').get('data', {})
        self.assertTrue('reels_media' in results)
