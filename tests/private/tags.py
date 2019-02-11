# -*- coding: utf-8 -*-

import time
from ..common import ApiTestBase, compat_mock, compat_urllib_parse


class TagsTests(ApiTestBase):
    """Tests for TagsEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_tag_info',
                'test': TagsTests('test_tag_info', api)
            },
            {
                'name': 'test_tag_related',
                'test': TagsTests('test_tag_related', api)
            },
            {
                'name': 'test_tag_search',
                'test': TagsTests('test_tag_search', api)
            },
            {
                'name': 'test_tag_follow_suggestions',
                'test': TagsTests('test_tag_follow_suggestions', api)
            },
            {
                'name': 'test_tags_user_following',
                'test': TagsTests('test_tags_user_following', api, user_id='25025320')
            },
            {
                'name': 'test_tag_follow_mock',
                'test': TagsTests('test_tag_follow_mock', api)
            },
            {
                'name': 'test_tag_unfollow_mock',
                'test': TagsTests('test_tag_unfollow_mock', api)
            },
            {
                'name': 'test_tag_section',
                'test': TagsTests('test_tag_section', api)
            },
        ]

    def test_tag_info(self):
        results = self.api.tag_info('catsofinstagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(results.get('media_count'), 0, 'No media_count returned.')

        time.sleep(self.sleep_interval)

        results = self.api.tag_info(u'日本')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(results.get('media_count'), 0, 'No media_count returned.')

    def test_tag_related(self):
        results = self.api.tag_related('catsofinstagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('related', [])), 0, 'No media_count returned.')

    def test_tag_search(self):
        rank_token = self.api.generate_uuid()
        results = self.api.tag_search('cats', rank_token)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('results', [])), 0, 'No results returned.')

    def test_tag_follow_suggestions(self):
        results = self.api.tag_follow_suggestions()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('tags', [])), 0, 'No results returned.')

    def test_tags_user_following(self):
        results = self.api.tags_user_following(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIn('tags', results)
        self.assertGreater(len(results.get('tags', [])), 0, 'No results returned.')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_tag_follow_mock(self, call_api):
        tag = 'catsofinstagram'
        call_api.return_value = {
            'status': 'ok',
        }
        self.api.tag_follow(tag)
        call_api.assert_called_with(
            'tags/follow/{hashtag!s}/'.format(
                hashtag=compat_urllib_parse.quote(tag.encode('utf-8'))),
            params=self.api.authenticated_params)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_tag_unfollow_mock(self, call_api):
        tag = 'catsofinstagram'
        call_api.return_value = {
            'status': 'ok',
        }
        self.api.tag_unfollow(tag)
        call_api.assert_called_with(
            'tags/unfollow/{hashtag!s}/'.format(
                hashtag=compat_urllib_parse.quote(tag.encode('utf-8'))),
            params=self.api.authenticated_params)

    def test_tag_section(self):
        results = self.api.tag_section('catsofinstagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIn('sections', results)
        self.assertGreater(len(results.get('sections', [])), 0, 'No results returned.')
