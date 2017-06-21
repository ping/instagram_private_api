import unittest

from ..common import (
    ApiTestBase, compat_mock, gen_user_breadcrumb
)


class LiveTests(ApiTestBase):
    """Tests for LiveEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_suggested_broadcasts',
                'test': LiveTests('test_suggested_broadcasts', api)
            },
            {
                'name': 'test_user_broadcast',
                'test': LiveTests('test_user_broadcast', api)
            },
            {
                'name': 'test_broadcast_info',
                'test': LiveTests('test_broadcast_info', api)
            },
            {
                'name': 'test_broadcast_comments',
                'test': LiveTests('test_broadcast_comments', api)
            },
            {
                'name': 'test_broadcast_heartbeat_and_viewercount',
                'test': LiveTests('test_broadcast_heartbeat_and_viewercount', api)
            },
            {
                'name': 'test_broadcast_like_count',
                'test': LiveTests('test_broadcast_like_count', api)
            },
            {
                'name': 'test_broadcast_like',
                'test': LiveTests('test_broadcast_like', api)
            },
            {
                'name': 'test_broadcast_like_mock',
                'test': LiveTests('test_broadcast_like_mock', api)
            },
            {
                'name': 'test_broadcast_comment',
                'test': LiveTests('test_broadcast_comment', api)
            },
            {
                'name': 'test_broadcast_comment_mock',
                'test': LiveTests('test_broadcast_comment_mock', api)
            },
            {
                'name': 'test_replay_broadcast_comments_mock',
                'test': LiveTests('test_replay_broadcast_comments_mock', api)
            },
            {
                'name': 'test_replay_broadcast_likes_mock',
                'test': LiveTests('test_replay_broadcast_likes_mock', api)
            },
        ]

    def test_user_broadcast(self):
        broadcast = self.api.user_broadcast('25025320')     # Instagram
        self.assertIsNone(broadcast)

    @unittest.skip('Modifies data.')
    def test_broadcast_like(self):
        top_live_results = self.api.discover_top_live()
        for b in top_live_results.get('broadcasts', []):
            if b['broadcast_status'] != 'active':
                continue
            broadcast_id = b['id']
            results = self.api.broadcast_like(broadcast_id)
            self.assertEqual(results.get('status'), 'ok')
            self.assertIsNotNone(results.get('likes'))
            break

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_broadcast_like_mock(self, call_api):
        broadcast_id = 123
        call_api.return_value = {'status': 'ok'}

        like_count = 2
        params = {'user_like_count': str(like_count)}
        params.update(self.api.authenticated_params)
        self.api.broadcast_like(broadcast_id, like_count)
        call_api.assert_called_with(
            'live/{broadcast_id!s}/like/'.format(**{'broadcast_id': broadcast_id}),
            params=params)

    def test_broadcast_like_count(self):
        top_live_results = self.api.discover_top_live()
        for b in top_live_results.get('broadcasts', []):
            if b['broadcast_status'] != 'active':
                continue
            broadcast_id = b['id']
            results = self.api.broadcast_like_count(broadcast_id)
            self.assertEqual(results.get('status'), 'ok')
            self.assertIsNotNone(results.get('likes'))
            self.assertIsNotNone(results.get('like_ts'))
            break

    def test_broadcast_comments(self):
        top_live_results = self.api.discover_top_live()
        for b in top_live_results.get('broadcasts', []):
            if b['broadcast_status'] != 'active':
                continue
            broadcast_id = b['id']
            results = self.api.broadcast_comments(broadcast_id)
            self.assertEqual(results.get('status'), 'ok')
            self.assertGreater(len(results.get('comments', [])), 0, 'No comments returned.')
            break

    def test_broadcast_heartbeat_and_viewercount(self):
        top_live_results = self.api.discover_top_live()
        for b in top_live_results.get('broadcasts', []):
            if b['broadcast_status'] != 'active':
                continue
            broadcast_id = b['id']
            results = self.api.broadcast_heartbeat_and_viewercount(broadcast_id)
            self.assertEqual(results.get('status'), 'ok')
            self.assertIsNotNone(results.get('viewer_count'))
            self.assertIsNotNone(results.get('broadcast_status'))
            break

    @unittest.skip('Modifies data.')
    def test_broadcast_comment(self):
        top_live_results = self.api.discover_top_live()
        for b in top_live_results.get('broadcasts', []):
            if b['broadcast_status'] != 'active':
                continue
            broadcast_id = b['id']
            results = self.api.broadcast_comment(broadcast_id, '...')
            self.assertEqual(results.get('status'), 'ok')
            self.assertIsNotNone(results.get('comment'))
            break

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_broadcast_comment_mock(self, call_api):
        broadcast_id = 123
        call_api.return_value = {'status': 'ok'}

        comment_text = '<3'
        breadcrumb = gen_user_breadcrumb(len(comment_text))
        generated_uuid = self.api.generate_uuid()
        with compat_mock.patch('instagram_private_api.endpoints.live.gen_user_breadcrumb') \
                as gen_user_breadcrumb_mock, \
                compat_mock.patch('instagram_private_api.Client.generate_uuid') \
                as generate_uuid_mock:
            gen_user_breadcrumb_mock.return_value = breadcrumb
            generate_uuid_mock.return_value = generated_uuid
            params = {
                'live_or_vod': '1',
                'offset_to_video_start': '0',
                'comment_text': comment_text,
                'user_breadcrumb': breadcrumb,
                'idempotence_token': generated_uuid,
            }
            params.update(self.api.authenticated_params)
            self.api.broadcast_comment(broadcast_id, comment_text)
            call_api.assert_called_with(
                'live/{broadcast_id!s}/comment/'.format(**{'broadcast_id': broadcast_id}),
                params=params)

    def test_broadcast_info(self):
        top_live_results = self.api.discover_top_live()
        for b in top_live_results.get('broadcasts', []):
            if b['broadcast_status'] != 'active':
                continue
            broadcast_id = b['id']
            results = self.api.broadcast_info(broadcast_id)
            self.assertEqual(results.get('status'), 'ok')
            self.assertIsNotNone(results.get('id'))
            self.assertIsNotNone(results.get('broadcast_owner'))
            self.assertIsNotNone(results.get('published_time'))
            self.assertIsNotNone(results.get('dash_playback_url'))
            break

    def test_suggested_broadcasts(self):
        results = self.api.suggested_broadcasts()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('broadcasts', [])), 0, 'No broadcasts returned.')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_replay_broadcast_comments_mock(self, call_api):
        broadcast_id = 123
        query = {
            'starting_offset': 0,
            'encoding_tag': 'instagram_dash_remuxed',
        }
        self.api.replay_broadcast_comments(broadcast_id, **query)
        call_api.assert_called_with(
            'live/{broadcast_id!s}/get_post_live_comments/'.format(**{'broadcast_id': broadcast_id}),
            query=query)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_replay_broadcast_likes_mock(self, call_api):
        broadcast_id = 123
        query = {
            'starting_offset': 0,
            'encoding_tag': 'instagram_dash_remuxed',
        }
        self.api.replay_broadcast_likes(broadcast_id, **query)
        call_api.assert_called_with(
            'live/{broadcast_id!s}/get_post_live_likes/'.format(**{'broadcast_id': broadcast_id}),
            query=query)
