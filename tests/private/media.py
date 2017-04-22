import unittest
import json

from ..common import (
    ClientError,
    ApiTestBase, compat_mock, gen_user_breadcrumb
)


class MediaTests(ApiTestBase):

    @classmethod
    def init_all(cls, api):
        return [
            {
                'name': 'test_media_info',
                'test': MediaTests('test_media_info', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_medias_info',
                'test': MediaTests('test_medias_info', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_media_permalink',
                'test': MediaTests('test_media_permalink', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_deleted_media_info',
                'test': MediaTests('test_deleted_media_info', api, media_id='1291110080498251995_329452045')
            },
            {
                'name': 'test_media_comments',
                'test': MediaTests('test_media_comments', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_deleted_media_comments',
                'test': MediaTests('test_deleted_media_comments', api, media_id='1291110080498251995_329452045')
            },
            {
                'name': 'test_media_n_comments',
                'test': MediaTests('test_media_n_comments', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_media_likers',
                'test': MediaTests('test_media_likers', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_media_likers_chrono',
                'test': MediaTests('test_media_likers_chrono', api, media_id='1206573574980690068_1497851591')
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
                'name': 'test_save_photo',
                'test': MediaTests('test_save_photo', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_save_photo_mock',
                'test': MediaTests('test_save_photo_mock', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_unsave_photo',
                'test': MediaTests('test_unsave_photo', api, media_id='1206573574980690068_1497851591')
            },
            {
                'name': 'test_unsave_photo_mock',
                'test': MediaTests('test_unsave_photo_mock', api, media_id='1206573574980690068_1497851591')
            },
        ]

    def test_media_info(self):
        results = self.api.media_info(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(results.get('items', [])[0].get('id'), self.test_media_id)

    def test_medias_info(self):
        results = self.api.media_info(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(results.get('items', [])[0].get('id'), self.test_media_id)

    def test_deleted_media_info(self):
        def check_deleted_media():
            self.api.media_info(self.test_media_id)
        self.assertRaises(ClientError, check_deleted_media)

        try:
            check_deleted_media()
        except ClientError as e:
            self.assertEqual(e.code, 400)

    def test_media_permalink(self):
        results = self.api.media_permalink(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('permalink'), 'No permalink returned.')

    def test_media_comments(self):
        results = self.api.media_comments(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('comments', [])), 0, 'No items returned.')

    def test_deleted_media_comments(self):
        def check_deleted_media():
            self.api.media_comments(self.test_media_id)
        self.assertRaises(ClientError, check_deleted_media)

        try:
            check_deleted_media()
        except ClientError as e:
            self.assertEqual(e.code, 400)

    def test_media_n_comments(self):
        num_of_comments = 50
        results = self.api.media_n_comments(self.test_media_id, n=num_of_comments)
        self.assertGreaterEqual(len(results), num_of_comments, 'No comment returned.')

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
            'media/%(media_id)s/edit_media/' % {'media_id': media_id},
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
            'media/%(media_id)s/delete/' % {'media_id': media_id},
            params=params)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_post_comment_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'comment': {'created_at': '1234567890', 'pk': 100000,
                        'user': {'pk': 123, 'username': 'x', 'full_name': 'X', 'profile_pic_url': 'x.jpg'}}}
        media_id = '123_123'
        comment_text = '<3'
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
                'media/%(media_id)s/comment/' % {'media_id': media_id},
                params=params)

    @compat_mock.patch('instagram_private_api.Client._call_api')
    def test_delete_comment_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        comment_id = '123456'
        self.api.delete_comment(media_id, comment_id)
        call_api.assert_called_with(
            'media/%(media_id)s/comment/%(comment_id)s/delete/'
            % {'media_id': media_id, 'comment_id': comment_id},
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
            'media/%(media_id)s/like/' % {'media_id': media_id},
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
            'media/%(media_id)s/unlike/' % {'media_id': media_id},
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
            'media/%(comment_id)s/comment_like/' % {'comment_id': comment_id},
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
            'media/%(comment_id)s/comment_unlike/' % {'comment_id': comment_id},
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
            'media/%(media_id)s/save/' % {'media_id': self.test_media_id},
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
            'media/%(media_id)s/unsave/' % {'media_id': self.test_media_id},
            params=params)
