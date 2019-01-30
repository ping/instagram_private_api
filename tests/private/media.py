import unittest
import json
import time

from ..common import (
    ClientError,
    ApiTestBase, compat_mock, gen_user_breadcrumb
)


class MediaTests(ApiTestBase):
    """Tests for MediaEndpointsMixin."""

    @staticmethod
    def init_all(api):
        test_media_id = '1962809196194057623_25025320'
        return [
            {
                'name': 'test_media_info',
                'test': MediaTests('test_media_info', api, media_id=test_media_id)
            },
            {
                'name': 'test_media_info2',
                'test': MediaTests('test_media_info', api, media_id='1367271575733086073_2958144170')
            },
            {
                'name': 'test_medias_info',
                'test': MediaTests('test_medias_info', api, media_id=test_media_id)
            },
            {
                'name': 'test_media_permalink',
                'test': MediaTests('test_media_permalink', api, media_id=test_media_id)
            },
            {
                'name': 'test_deleted_media_info',
                'test': MediaTests('test_deleted_media_info', api, media_id='1291110080498251995_329452045')
            },
            {
                'name': 'test_media_comments',
                'test': MediaTests('test_media_comments', api, media_id=test_media_id)
            },
            {
                'name': 'test_deleted_media_comments',
                'test': MediaTests('test_deleted_media_comments', api, media_id='1291110080498251995_329452045')
            },
            {
                'name': 'test_media_n_comments',
                'test': MediaTests('test_media_n_comments', api, media_id=test_media_id)
            },
            {
                'name': 'test_media_likers',
                'test': MediaTests('test_media_likers', api, media_id=test_media_id)
            },
            {
                'name': 'test_media_likers_chrono',
                'test': MediaTests('test_media_likers_chrono', api, media_id=test_media_id)
            },
            {
                'name': 'test_comment_like',
                'test': MediaTests('test_comment_like', api)
            },
            {
                'name': 'test_comment_like_mock',
                'test': MediaTests('test_comment_like_mock', api)
            },
            {
                'name': 'test_comment_unlike',
                'test': MediaTests('test_comment_unlike', api)
            },
            {
                'name': 'test_comment_unlike_mock',
                'test': MediaTests('test_comment_unlike_mock', api)
            },
            {
                'name': 'test_comment_likers',
                'test': MediaTests('test_comment_likers', api)
            },
            {
                'name': 'test_edit_media',
                'test': MediaTests('test_edit_media', api)
            },
            {
                'name': 'test_edit_media_mock',
                'test': MediaTests('test_edit_media_mock', api)
            },
            {
                'name': 'test_delete_media',
                'test': MediaTests('test_delete_media', api)
            },
            {
                'name': 'test_delete_media_mock',
                'test': MediaTests('test_delete_media_mock', api)
            },
            {
                'name': 'test_post_like',
                'test': MediaTests('test_post_like', api)
            },
            {
                'name': 'test_post_like_mock',
                'test': MediaTests('test_post_like_mock', api)
            },
            {
                'name': 'test_delete_like',
                'test': MediaTests('test_delete_like', api)
            },
            {
                'name': 'test_delete_like_mock',
                'test': MediaTests('test_delete_like_mock', api)
            },
            {
                'name': 'test_post_comment_mock',
                'test': MediaTests('test_post_comment_mock', api)
            },
            {
                'name': 'test_delete_comment_mock',
                'test': MediaTests('test_delete_comment_mock', api)
            },
            {
                'name': 'test_bulk_delete_comments_mock',
                'test': MediaTests('test_bulk_delete_comments_mock', api)
            },
            {
                'name': 'test_save_photo',
                'test': MediaTests('test_save_photo', api, media_id=test_media_id)
            },
            {
                'name': 'test_save_photo_mock',
                'test': MediaTests('test_save_photo_mock', api, media_id=test_media_id)
            },
            {
                'name': 'test_unsave_photo',
                'test': MediaTests('test_unsave_photo', api, media_id=test_media_id)
            },
            {
                'name': 'test_unsave_photo_mock',
                'test': MediaTests('test_unsave_photo_mock', api, media_id=test_media_id)
            },
            {
                'name': 'test_disable_comments_mock',
                'test': MediaTests('test_disable_comments_mock', api)
            },
            {
                'name': 'test_enable_comments_mock',
                'test': MediaTests('test_enable_comments_mock', api)
            },
            {
                'name': 'test_media_seen',
                'test': MediaTests('test_media_seen', api)
            },
            {
                'name': 'test_media_seen_mock',
                'test': MediaTests('test_media_seen_mock', api)
            },
            {
                'name': 'test_media_seen2_mock',
                'test': MediaTests('test_media_seen2_mock', api)
            },
            {
                'name': 'test_media_only_me',
                'test': MediaTests('test_media_only_me', api)
            },
            {
                'name': 'test_media_only_me_mock',
                'test': MediaTests('test_media_only_me_mock', api)
            },
            {
                'name': 'test_comment_replies',
                'test': MediaTests('test_comment_replies', api)
            },
            {
                'name': 'test_comment_inline_replies',
                'test': MediaTests('test_comment_inline_replies', api)
            },
            {
                'name': 'test_story_viewers_mock',
                'test': MediaTests('test_story_viewers_mock', api)
            },
            {
                'name': 'test_story_viewers',
                'test': MediaTests('test_story_viewers', api)
            },
        ]

    def test_media_info(self):
        results = self.api.media_info(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(results.get('items', [])[0].get('id'), self.test_media_id)
        video_versions = results.get('items', [])[0].get('video_versions')
        if video_versions:
            videos = sorted(video_versions, key=lambda m: m['width'], reverse=True)
            self.assertGreaterEqual(videos[0]['width'], 640, 'High res video not retrieved.')

    def test_medias_info(self):
        results = self.api.medias_info([self.test_media_id])
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(results.get('items', [])[0].get('id'), self.test_media_id)

    def test_deleted_media_info(self):
        with self.assertRaises(ClientError) as ce:
            self.api.media_info(self.test_media_id)
        self.assertEqual(ce.exception.code, 400)

    def test_media_permalink(self):
        results = self.api.media_permalink(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('permalink'), 'No permalink returned.')

    def test_media_comments(self):
        results = self.api.media_comments(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('comments', [])), 0, 'No items returned.')

    def test_deleted_media_comments(self):
        with self.assertRaises(ClientError) as ce:
            self.api.media_comments(self.test_media_id)
        self.assertEqual(ce.exception.code, 400)

    def test_media_n_comments(self):
        num_of_comments = 50
        results = self.api.media_n_comments(self.test_media_id, n=num_of_comments)
        self.assertGreaterEqual(len(results), num_of_comments, 'No comment returned.')

    def test_comment_replies(self):
        results = self.api.comment_replies(
            '1652531711743017348_184692323', '17881229782160892')
        self.assertGreater(
            len(results.get('child_comments', [])), 0, 'No replies returned.')

    def test_comment_inline_replies(self):
        results = self.api.comment_inline_replies(
            # max_id should not be '' but...
            '1652531711743017348_184692323', '17881229782160892', max_id='')
        self.assertGreater(
            len(results.get('child_comments', [])), 0, 'No replies returned.')

    @unittest.skip('Modifies data.')
    def test_edit_media(self):
        results = self.api.self_feed()
        items = results.get('items', [])
        results = self.api.edit_media(items[0]['id'], 'Hello')
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_edit_media_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'media': {
                'pk': 123, 'code': 'abc', 'taken_at': 1234567890,
                'media_type': 1, 'caption': None,
                'user': {
                    'pk': 123, 'biography': '',
                    'profile_pic_url': 'https://example.com/x.jpg',
                    'external_url': ''
                }
            }
        }
        media_id = '123_123'
        caption = 'Hello'
        params = {'caption_text': caption}
        params.update(self.api.authenticated_params)
        self.api.edit_media(media_id, 'Hello')
        call_api.assert_called_with(
            'media/{media_id!s}/edit_media/'.format(**{'media_id': media_id}),
            params=params)

    @unittest.skip('Modifies data.')
    def test_delete_media(self):
        results = self.api.self_feed()
        items = results.get('items', [])
        results = self.api.delete_media(items[0]['id'])
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_delete_media_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        params = {'media_id': media_id}
        params.update(self.api.authenticated_params)
        self.api.delete_media(media_id)
        call_api.assert_called_with(
            'media/{media_id!s}/delete/'.format(**{'media_id': media_id}),
            params=params)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_post_comment_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'comment': {'created_at': '1234567890', 'pk': 100000,
                        'user': {'pk': 123, 'username': 'x', 'full_name': 'X', 'profile_pic_url': 'x.jpg'}}}
        media_id = '123_123'
        comment_text = '<3 #heart https://google.com'
        breadcrumb = gen_user_breadcrumb(len(comment_text))
        generated_uuid = self.api.generate_uuid()
        with compat_mock.patch('instagram_private_api.endpoints.media.gen_user_breadcrumb') \
                as gen_user_breadcrumb_mock, \
                compat_mock.patch('instagram_private_api.Client.generate_uuid')\
                as generate_uuid_mock:
            gen_user_breadcrumb_mock.return_value = breadcrumb
            generate_uuid_mock.return_value = generated_uuid
            params = {
                'comment_text': comment_text,
                'user_breadcrumb': breadcrumb,
                'idempotence_token': generated_uuid,
                'containermodule': 'comments_feed_timeline',
                'radio_type': self.api.radio_type,
            }
            params.update(self.api.authenticated_params)
            self.api.post_comment(media_id, comment_text)
            call_api.assert_called_with(
                'media/{media_id!s}/comment/'.format(**{'media_id': media_id}),
                params=params)

        test_comments = [
            'x' * 301,      # Test max length
            'X' * 300,      # Test all caps
            '#test #test #test #test #test'     # Test hashtags limit
            'https://google.com http://google.com'      # Test urls limit
        ]
        for t in test_comments:
            with self.assertRaises(ValueError):
                self.api.post_comment(media_id, t)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_delete_comment_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        comment_id = '123456'
        self.api.delete_comment(media_id, comment_id)
        call_api.assert_called_with(
            'media/{media_id!s}/comment/{comment_id!s}/delete/'.format(
                **{'media_id': media_id, 'comment_id': comment_id}),
            params=self.api.authenticated_params)

    def test_media_likers(self):
        results = self.api.media_likers(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No items returned.')

    def test_media_likers_chrono(self):
        results = self.api.media_likers_chrono(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No items returned.')

    @unittest.skip('Modifies data.')
    def test_post_like(self):
        results = self.api.post_like('1486470123929723160_25025320')
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_post_like_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        params = {
            'media_id': media_id,
            'module_name': 'x',
            'radio_type': self.api.radio_type,
        }
        params.update(self.api.authenticated_params)
        self.api.post_like(media_id, params['module_name'])
        call_api.assert_called_with(
            'media/{media_id!s}/like/'.format(**{'media_id': media_id}),
            query={'d': '1'},
            params=params)

    @unittest.skip('Modifies data.')
    def test_delete_like(self):
        results = self.api.delete_like('1486470123929723160_25025320')
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_delete_like_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        params = {
            'media_id': media_id,
            'module_name': 'x',
            'radio_type': self.api.radio_type,
        }
        params.update(self.api.authenticated_params)
        self.api.delete_like(media_id, params['module_name'])
        call_api.assert_called_with(
            'media/{media_id!s}/unlike/'.format(**{'media_id': media_id}),
            params=params)

    @unittest.skip('Modifies data.')
    def test_comment_like(self):
        results = self.api.comment_like('17852927593096945')
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_comment_like_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        comment_id = '1785000000000'
        self.api.comment_like(comment_id)
        call_api.assert_called_with(
            'media/{comment_id!s}/comment_like/'.format(**{'comment_id': comment_id}),
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_comment_unlike(self):
        results = self.api.comment_unlike('17852927593096945')
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_comment_unlike_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        comment_id = '1785000000000'
        self.api.comment_unlike(comment_id)
        call_api.assert_called_with(
            'media/{comment_id!s}/comment_unlike/'.format(**{'comment_id': comment_id}),
            params=self.api.authenticated_params)

    def test_comment_likers(self):
        results = self.api.comment_likers('17852927593096945')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('users'))

    @unittest.skip('Modifies data.')
    def test_save_photo(self):
        results = self.api.save_photo(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_save_photo_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        added_collection_ids = ['1234567890']
        params = {
            'radio_type': self.api.radio_type,
            'added_collection_ids': json.dumps(added_collection_ids, separators=(',', ':'))
        }
        params.update(self.api.authenticated_params)
        self.api.save_photo(self.test_media_id, added_collection_ids=added_collection_ids)
        call_api.assert_called_with(
            'media/{media_id!s}/save/'.format(**{'media_id': self.test_media_id}),
            params=params)

    @unittest.skip('Modifies data.')
    def test_unsave_photo(self):
        results = self.api.unsave_photo(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_unsave_photo_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        removed_collection_ids = ['1234567890']
        params = {
            'radio_type': self.api.radio_type,
            'removed_collection_ids': json.dumps(removed_collection_ids, separators=(',', ':'))
        }
        params.update(self.api.authenticated_params)
        self.api.unsave_photo(self.test_media_id, removed_collection_ids=removed_collection_ids)
        call_api.assert_called_with(
            'media/{media_id!s}/unsave/'.format(**{'media_id': self.test_media_id}),
            params=params)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_disable_comments_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        params = {
            '_csrftoken': self.api.csrftoken,
            '_uuid': self.api.uuid
        }
        self.api.disable_comments(self.test_media_id)
        call_api.assert_called_with(
            'media/{media_id!s}/disable_comments/'.format(**{'media_id': self.test_media_id}),
            params=params, unsigned=True)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_enable_comments_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        params = {
            '_csrftoken': self.api.csrftoken,
            '_uuid': self.api.uuid
        }
        self.api.enable_comments(self.test_media_id)
        call_api.assert_called_with(
            'media/{media_id!s}/enable_comments/'.format(**{'media_id': self.test_media_id}),
            params=params, unsigned=True)

    @unittest.skip('Modifies data.')
    def test_media_seen(self, call_api):
        reels_media_results = self.api.reels_media(['25025320'])
        if not reels_media_results.get('reels_media'):
            return
        reels_media = reels_media_results['reels_media'][0]['items']
        results = self.api.media_seen(reels_media)
        self.assertEqual(results['status'], 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_media_seen_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        params = {
            'reels': {
                '1309764653429046112_124317_124317': ['1470356135_1470372049'],
                '1309209597843679372_124317_124317': ['1470289967_1470372013']},
        }
        params.update(self.api.authenticated_params)
        self.api.media_seen(params['reels'])
        call_api.assert_called_with(
            'media/seen/', params=params, version='v2')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_media_seen2_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        ts_now = 1493789777

        with compat_mock.patch('instagram_private_api.endpoints.media.randint') as randint_mock, \
                compat_mock.patch('instagram_private_api.endpoints.media.time.time') as time_mock:

            time_mock.return_value = ts_now
            randint_mock.return_value = 0
            params = {
                'reels': {
                    '1309764653429046112_124317_124317': ['1470356135_{0!s}'.format((int(ts_now) - 1))],
                    '1309209597843679372_124317_124317': ['1470289967_{0!s}'.format((int(ts_now) - 2))]},
            }
            reels_params = [
                {'id': '1309764653429046112_124317', 'taken_at': 1470356135, 'user': {'pk': 124317}},
                {'id': '1309209597843679372_124317', 'taken_at': 1470289967, 'user': {'pk': 124317}}
            ]
            params.update(self.api.authenticated_params)
            self.api.media_seen(reels_params)
            call_api.assert_called_with(
                'media/seen/', params=params, version='v2')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_bulk_delete_comments_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        comment_ids = ['123456', '7890123']
        params = {
            'comment_ids_to_delete': ','.join(comment_ids)
        }
        params.update(self.api.authenticated_params)
        self.api.bulk_delete_comments(media_id, comment_ids)
        call_api.assert_called_with(
            'media/{media_id!s}/comment/bulk_delete/'.format(**{'media_id': media_id}),
            params=params)

    @unittest.skip('Modifies data.')
    def test_media_only_me(self):
        results = self.api.self_feed()
        first_media = results.get('items', [{}])[0]
        time.sleep(self.sleep_interval)

        results = self.api.media_only_me(first_media['id'], first_media['media_type'])
        self.assertEqual(results.get('status'), 'ok')
        time.sleep(self.sleep_interval)

        results = self.api.media_only_me(
            first_media['id'], first_media['media_type'], undo=True)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_media_only_me_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        params = {
            'media_id': media_id
        }
        params.update(self.api.authenticated_params)
        self.api.media_only_me(media_id, 2)
        call_api.assert_called_with(
            'media/{media_id!s}/only_me/'.format(**{'media_id': media_id}),
            params=params, query={'media_type': 2})

        self.api.media_only_me(media_id, 2, undo=True)
        call_api.assert_called_with(
            'media/{media_id!s}/undo_only_me/'.format(**{'media_id': media_id}),
            params=params, query={'media_type': 2})

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_story_viewers_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        story_pk = '170000000'
        self.api.story_viewers(story_pk)
        call_api.assert_called_with(
            'media/{story_pk!s}/list_reel_media_viewer/'.format(story_pk=story_pk),
            query={})

    @unittest.skip('Requires valid story PK.')
    def test_story_viewers(self):
        results = self.api.story_viewers('170000000123')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIn('users', results)
        self.assertIn('total_viewer_count', results)
        self.assertIn('user_count', results)
