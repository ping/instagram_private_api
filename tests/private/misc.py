import unittest

from ..common import ApiTestBase


class MiscTests(ApiTestBase):
    """Tests for MiscEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_sync',
                'test': MiscTests('test_sync', api)
            },
            {
                'name': 'test_ranked_recipients',
                'test': MiscTests('test_ranked_recipients', api)
            },
            {
                'name': 'test_recent_recipients',
                'test': MiscTests('test_recent_recipients', api)
            },
            {
                'name': 'test_news',
                'test': MiscTests('test_news', api)
            },
            {
                'name': 'test_news_inbox',
                'test': MiscTests('test_news_inbox', api)
            },
            {
                'name': 'test_direct_v2_inbox',
                'test': MiscTests('test_direct_v2_inbox', api)
            },
            {
                'name': 'test_oembed',
                'test': MiscTests('test_oembed', api)
            },
            {
                'name': 'test_bulk_translate',
                'test': MiscTests('test_bulk_translate', api)
            },
            {
                'name': 'test_translate',
                'test': MiscTests('test_translate', api)
            },
            {
                'name': 'test_megaphone_log',
                'test': MiscTests('test_megaphone_log', api)
            },
            {
                'name': 'test_expose',
                'test': MiscTests('test_expose', api)
            },
            {
                'name': 'test_top_search',
                'test': MiscTests('test_top_search', api)
            },
            {
                'name': 'test_stickers',
                'test': MiscTests('test_stickers', api)
            },
        ]

    def test_sync(self):
        results = self.api.sync()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('experiments', [])), 0, 'No experiments returned.')

    @unittest.skip('Deprecated.')
    def test_expose(self):
        results = self.api.expose()
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Posts data')
    def test_megaphone_log(self):
        results = self.api.megaphone_log('turn_on_push')
        self.assertEqual(results.get('status'), 'ok')
        self.assertTrue(results.get('success'))

    def test_ranked_recipients(self):
        results = self.api.ranked_recipients()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('ranked_recipients'))

    def test_recent_recipients(self):
        results = self.api.recent_recipients()
        self.assertEqual(results.get('status'), 'ok')

    def test_news(self):
        results = self.api.news()
        self.assertEqual(results.get('status'), 'ok')

    def test_news_inbox(self):
        results = self.api.news_inbox()
        self.assertEqual(results.get('status'), 'ok')

    def test_direct_v2_inbox(self):
        results = self.api.direct_v2_inbox()
        self.assertEqual(results.get('status'), 'ok')

    def test_oembed(self):
        results = self.api.oembed('https://www.instagram.com/p/BJL-gjsDyo1/')
        self.assertIsNotNone(results.get('html'))

    def test_translate(self):
        results = self.api.translate('1390480622', '3')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('translation'))

    def test_bulk_translate(self):
        results = self.api.bulk_translate('17851953262114589')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('comment_translations', [])), 0, 'No translations returned.')

    def test_top_search(self):
        results = self.api.top_search('cats')
        self.assertEqual(results.get('status'), 'ok')

    def test_stickers(self):
        results = self.api.stickers(location={'lat': '40.7484445', 'lng': '-73.9878531', 'horizontalAccuracy': 5.8})
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('static_stickers'))

        self.assertRaises(ValueError, lambda: self.api.stickers('x'))
        self.assertRaises(ValueError, lambda: self.api.stickers(location={'x': 1}))
