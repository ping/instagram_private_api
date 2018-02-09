import json

from ..common import (
    ApiTestBase, compat_mock
)


class HighlightsTests(ApiTestBase):
    """Tests for HighlightsEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_stories_archive',
                'test': HighlightsTests('test_stories_archive', api)
            },
            {
                'name': 'test_highlights_user_feed',
                'test': HighlightsTests('test_highlights_user_feed', api, user_id='25025320')
            },
            {
                'name': 'test_highlight_create_mock',
                'test': HighlightsTests('test_highlight_create_mock', api)
            },
            {
                'name': 'test_highlight_edit_mock',
                'test': HighlightsTests('test_highlight_edit_mock', api)
            },
            {
                'name': 'test_highlight_delete_mock',
                'test': HighlightsTests('test_highlight_delete_mock', api)
            },
        ]

    def test_stories_archive(self):
        results = self.api.stories_archive()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIn('items', results)

    def test_highlights_user_feed(self):
        results = self.api.highlights_user_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIn('tray', results)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_highlight_create_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok', 'reel': {
                'id': 'highlight:1710000000'
            }
        }
        media_ids = ['123456700_001', '123456701_001']

        cover = {
            'media_id': media_ids[0],
            'crop_rect': json.dumps(
                [0.0, 0.21830457, 1.0, 0.78094524], separators=(',', ':'))
        }
        params = {
            'media_ids': json.dumps(media_ids, separators=(',', ':')),
            'cover': json.dumps(cover, separators=(',', ':')),
            'source': 'x',
            'title': 'Test',
        }
        params.update(self.api.authenticated_params)

        self.api.highlight_create(
            media_ids, title=params['title'], source=params['source'])
        call_api.assert_called_with(
            'highlights/create_reel/',
            params=params)

        with self.assertRaises(ValueError):
            self.api.highlight_create(
                media_ids, title='A title that is much too long'
            )

        with self.assertRaises(ValueError):
            self.api.highlight_create('x')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_highlight_edit_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok', 'reel': {
                'id': 'highlight:1710000000'
            }
        }
        highlight_id = 'highlight:123456'
        endpoint = 'highlights/{highlight_id!s}/edit_reel/'.format(
            highlight_id=highlight_id
        )

        cover = {
            'media_id': '123456789_001',
            'crop_rect': json.dumps(
                [0.0, 0.21830457, 1.0, 0.78094524], separators=(',', ':'))
        }
        params = {
            'added_media_ids': json.dumps([], separators=(',', ':')),
            'removed_media_ids': json.dumps([], separators=(',', ':')),
            'cover': json.dumps(cover, separators=(',', ':')),
            'source': 'x',
            'title': 'Test',
        }
        params.update(self.api.authenticated_params)

        with self.assertRaises(ValueError):
            # test empty edit
            self.api.highlight_edit(highlight_id)

        self.api.highlight_edit(
            highlight_id, cover_media_id=cover['media_id'],
            added_media_ids=[], removed_media_ids=[],
            title=params['title'], source=params['source'])
        call_api.assert_called_with(endpoint, params=params)

        with self.assertRaises(ValueError):
            self.api.highlight_edit(
                highlight_id, title='A title that is much too long'
            )

        with self.assertRaises(ValueError):
            self.api.highlight_edit(
                highlight_id, added_media_ids='x'
            )

        with self.assertRaises(ValueError):
            self.api.highlight_edit(
                highlight_id, removed_media_ids='x'
            )

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_highlight_delete_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}

        highlight_id = 'highlight:1000'
        endpoint = 'highlights/{highlight_id!s}/delete_reel/'.format(
            highlight_id=highlight_id
        )
        self.api.highlight_delete(highlight_id)
        call_api.assert_called_with(
            endpoint, params=self.api.authenticated_params)
