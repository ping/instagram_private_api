import unittest

from ..common import ApiTestBase, ClientError


class FeedTests(ApiTestBase):
    """Tests for FeedEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_feed_timeline',
                'test': FeedTests('test_feed_timeline', api)
            },
            {
                'name': 'test_feed_liked',
                'test': FeedTests('test_feed_liked', api)
            },
            {
                'name': 'test_self_feed',
                'test': FeedTests('test_self_feed', api)
            },
            {
                'name': 'test_user_feed',
                'test': FeedTests('test_user_feed', api, user_id='124317')
            },
            {
                'name': 'test_username_feed',
                'test': FeedTests('test_username_feed', api, user_id='maruhanamogu')
            },
            {
                'name': 'test_private_user_feed',
                'test': FeedTests('test_private_user_feed', api, user_id='426095486')
            },
            {
                'name': 'test_reels_tray',
                'test': FeedTests('test_reels_tray', api)
            },
            {
                'name': 'test_user_reel_media',
                'test': FeedTests('test_user_reel_media', api, user_id='329452045')
            },
            {
                'name': 'test_reels_media',
                'test': FeedTests('test_reels_media', api, user_id='329452045')
            },
            {
                'name': 'test_user_story_feed',
                'test': FeedTests('test_user_story_feed', api, user_id='329452045')
            },
            {
                'name': 'test_location_feed',
                'test': FeedTests('test_location_feed', api)
            },
            {
                'name': 'test_feed_tag',
                'test': FeedTests('test_feed_tag', api)
            },
            {
                'name': 'test_saved_feed',
                'test': FeedTests('test_saved_feed', api)
            },
            {
                'name': 'test_feed_popular',
                'test': FeedTests('test_feed_popular', api)
            },
            {
                'name': 'test_feed_only_me',
                'test': FeedTests('test_feed_only_me', api)
            },
        ]

    def test_feed_liked(self):
        results = self.api.feed_liked()
        self.assertEqual(results.get('status'), 'ok')

    def test_feed_timeline(self):
        results = self.api.feed_timeline()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('feed_items', [])), 0, 'No items returned.')
        self.assertIsNotNone(results.get('feed_items', [])[0]['media_or_ad'].get('link'))

    @unittest.skip('Deprecated.')
    def test_feed_popular(self):
        results = self.api.feed_popular()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_private_user_feed(self):
        with self.assertRaises(ClientError) as ce:
            self.api.user_feed(self.test_user_id)
        self.assertEqual(ce.exception.code, 400)

    def test_self_feed(self):
        results = self.api.self_feed()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_username_feed(self):
        results = self.api.username_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_reels_tray(self):
        results = self.api.reels_tray()
        self.assertEqual(results.get('status'), 'ok')

    def test_user_reel_media(self):
        results = self.api.user_reel_media(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    def test_reels_media(self):
        results = self.api.reels_media([self.test_user_id])
        self.assertEqual(results.get('status'), 'ok')

    def test_feed_tag(self):
        rank_token = self.api.generate_uuid()
        results = self.api.feed_tag('catsofinstagram', rank_token)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')
        self.assertGreater(len(results.get('ranked_items', [])), 0, 'No ranked_items returned.')
        if results.get('story'):    # Returned only in version >= 10.22.0
            self.assertGreater(len(results.get('story', {}).get('items', [])), 0, 'No story items returned.')

    def test_user_story_feed(self):
        results = self.api.user_story_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Deprecated.')
    def test_location_feed(self):
        rank_token = self.api.generate_uuid()
        # 213012122 - Yosemite National Park
        # 218551172247829 - Mount Fuji
        results = self.api.feed_location(218551172247829, rank_token)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')
        self.assertGreater(len(results.get('ranked_items', [])), 0, 'No ranked_items returned.')
        if results.get('story'):    # Returned only in version >= 10.22.0
            self.assertGreater(len(results.get('story', {}).get('items', [])), 0, 'No story items returned.')

    def test_saved_feed(self):
        results = self.api.saved_feed()
        self.assertEqual(results.get('status'), 'ok')

    def test_feed_only_me(self):
        results = self.api.feed_only_me()
        self.assertEqual(results.get('status'), 'ok')
