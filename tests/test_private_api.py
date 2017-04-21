import unittest
import argparse
import os
import time
import json
import copy
import sys
import logging
import re
import warnings
try:
    # python 2.x
    from urllib2 import urlopen
except ImportError:
    # python 3.x
    from urllib.request import urlopen
try:
    import unittest.mock as mock
except ImportError:
    import mock

try:
    from instagram_private_api import (
        __version__, Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientCompatPatch)
    from instagram_private_api.utils import (
        InstagramID, gen_user_breadcrumb,
        max_chunk_size_generator, max_chunk_count_generator
    )
    from instagram_private_api.constants import Constants
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        __version__, Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientCompatPatch)
    from instagram_private_api.utils import (
        InstagramID, gen_user_breadcrumb,
        max_chunk_size_generator, max_chunk_count_generator
    )
    from instagram_private_api.constants import Constants


class TestPrivateApi(unittest.TestCase):

    def __init__(self, testname, api, user_id=None, media_id=None):
        super(TestPrivateApi, self).__init__(testname)
        self.api = api
        self.test_user_id = user_id
        self.test_media_id = media_id

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        if not self._testMethodName.endswith('_mock'):
            time.sleep(2.5)   # sleep a bit between tests to avoid HTTP429 errors

    @unittest.skip('Unwise to run frequently.')
    def test_login(self):
        new_client = Client(self.api.username, self.api.password)
        self.assertEqual(new_client.authenticated_user_name, self.api.username)

    @mock.patch('instagram_private_api.Client.csrftoken',
                new_callable=mock.PropertyMock, return_value='abcde')
    def test_login_mock(self, csrftoken):
        generated_uuid = Client.generate_uuid(True)
        query = {'challenge_type': 'signup', 'guid': generated_uuid}
        with mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock, \
                mock.patch('instagram_private_api.Client._call_api') as call_api, \
                mock.patch('instagram_private_api.Client._read_response') as read_response:
            generate_uuid_mock.return_value = generated_uuid
            call_api.return_value = ''
            read_response.return_value = json.dumps({'status': 'ok', 'logged_in_user': {'pk': 123}})
            self.api.login()

            call_api.assert_any_call(
                'si/fetch_headers/', params='', query=query, return_response=True)

            login_params = {
                'device_id': self.api.device_id,
                'guid': self.api.uuid,
                'adid': self.api.ad_id,
                'phone_id': self.api.phone_id,
                '_csrftoken': self.api.csrftoken,
                'username': self.api.username,
                'password': self.api.password,
                'login_attempt_count': '0',
            }
            call_api.assert_called_with(
                'accounts/login/', params=login_params, return_response=True)

    @mock.patch('instagram_private_api.Client.csrftoken',
                new_callable=mock.PropertyMock, return_value=None)
    def test_login_failcsrf_mock(self, csrftoken):
        generated_uuid = Client.generate_uuid(True)
        with mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock, \
                mock.patch('instagram_private_api.Client._call_api') as call_api, \
                mock.patch('instagram_private_api.Client._read_response') as read_response:
            generate_uuid_mock.return_value = generated_uuid
            call_api.return_value = ''
            read_response.return_value = ''
            with self.assertRaises(ClientError) as tc:
                self.api.login()
            self.assertEqual(tc.exception.message, 'Unable to get csrf from login challenge.')

    @mock.patch('instagram_private_api.Client.csrftoken',
                new_callable=mock.PropertyMock, return_value='abcde')
    def test_login_fail_mock(self, csrftoken):
        generated_uuid = Client.generate_uuid(True)
        with mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock, \
                mock.patch('instagram_private_api.Client._call_api') as call_api, \
                mock.patch('instagram_private_api.Client._read_response') as read_response:
            generate_uuid_mock.return_value = generated_uuid
            call_api.return_value = ''
            read_response.return_value = json.dumps({'status': 'fail'})

            with self.assertRaises(ClientError) as tc:
                self.api.login()
            self.assertEqual(tc.exception.message, 'Unable to login.')

    def test_sync(self):
        results = self.api.sync()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('experiments', [])), 0, 'No experiments returned.')

    def test_current_user(self):
        results = self.api.current_user()
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(str(results.get('user', {}).get('pk', '')), self.api.authenticated_user_id)

    @unittest.skip('Heavily throttled.')
    def test_autocomplete_user_list(self):
        results = self.api.autocomplete_user_list()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No users returned.')

    def test_explore(self):
        results = self.api.explore()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

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

    def test_feed_liked(self):
        results = self.api.feed_liked()
        self.assertEqual(results.get('status'), 'ok')

    def test_user_info(self):
        results = self.api.user_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user', {}).get('profile_picture'))

    def test_username_info(self):
        results = self.api.username_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user', {}).get('profile_picture'))

    def test_feed_timeline(self):
        results = self.api.feed_timeline()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('feed_items', [])), 0, 'No items returned.')
        self.assertIsNotNone(results.get('feed_items', [])[0]['media_or_ad'].get('link'))

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

    def test_media_likers(self):
        results = self.api.media_likers(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No items returned.')

    def test_media_likers_chrono(self):
        results = self.api.media_likers_chrono(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No items returned.')

    def test_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_self_feed(self):
        results = self.api.self_feed()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_username_feed(self):
        results = self.api.username_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_private_user_feed(self):
        def check_private_user():
            self.api.user_feed(self.test_user_id)
        self.assertRaises(ClientError, check_private_user)

        try:
            check_private_user()
        except ClientError as e:
            self.assertEqual(e.code, 400)

    def test_user_detail_info(self):
        results = self.api.user_detail_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('feed', {}).get('items', [])), 0, 'No items returned.')

    def test_user_following(self):
        results = self.api.user_following(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No users returned.')
        self.assertIsNotNone(results.get('users', [])[0].get('id'), 'Is not patched.')

    def test_user_followers(self):
        results = self.api.user_followers(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No users returned.')
        self.assertIsNotNone(results.get('users', [])[0].get('id'), 'Is not patched.')

    def test_search_users(self):
        results = self.api.search_users('maruhanamogu')
        self.assertEqual(results.get('status'), 'ok')

    def test_oembed(self):
        results = self.api.oembed('https://www.instagram.com/p/BJL-gjsDyo1/')
        self.assertIsNotNone(results.get('html'))

    def test_reels_tray(self):
        results = self.api.reels_tray()
        self.assertEqual(results.get('status'), 'ok')

    def test_user_reel_media(self):
        results = self.api.user_reel_media(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    def test_reels_media(self):
        results = self.api.reels_media([self.test_user_id])
        self.assertEqual(results.get('status'), 'ok')

    def test_user_story_feed(self):
        results = self.api.user_story_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    def test_friendships_show(self):
        results = self.api.friendships_show(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')

    def test_friendships_show_many(self):
        results = self.api.friendships_show_many(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('friendship_statuses', [])), 0, 'No statuses returned.')

    def test_friendships_pending(self):
        results = self.api.friendships_pending()
        self.assertEqual(results.get('status'), 'ok')

    def test_bulk_translate(self):
        results = self.api.bulk_translate('17851953262114589')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('comment_translations', [])), 0, 'No translations returned.')

    def test_translate(self):
        results = self.api.translate('1390480622', '3')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('translation'))

    def test_feed_tag(self):
        results = self.api.feed_tag('catsofinstagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')
        self.assertGreater(len(results.get('ranked_items', [])), 0, 'No ranked_items returned.')

    def test_tag_info(self):
        results = self.api.tag_info('catsofinstagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(results.get('media_count'), 0, 'No media_count returned.')

    def test_tag_related(self):
        results = self.api.tag_related('catsofinstagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('related', [])), 0, 'No media_count returned.')

    def test_tag_search(self):
        results = self.api.tag_search('cats')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('results', [])), 0, 'No results returned.')

    def test_usertag_feed(self):
        results = self.api.usertag_feed(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_location_feed(self):
        results = self.api.feed_location(229573811)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')
        self.assertGreater(len(results.get('ranked_items', [])), 0, 'No ranked_items returned.')

    def test_location_info(self):
        results = self.api.location_info(229573811)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('location'))

    def test_location_related(self):
        results = self.api.location_related(229573811)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('related'))

    def test_location_search(self):
        results = self.api.location_search('40.7484445', '-73.9878531', query='Empire')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('venues', [])), 0, 'No venues returned.')

    def test_location_fb_search(self):
        results = self.api.location_fb_search('Paris, France')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_discover_top_live(self):
        results = self.api.discover_top_live()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('broadcasts', [])), 0, 'No broadcasts returned.')

    def test_suggested_broadcasts(self):
        results = self.api.suggested_broadcasts()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('broadcasts', [])), 0, 'No broadcasts returned.')

    def test_top_live_status(self):
        results = self.api.discover_top_live()
        broadcast_ids = [b['id'] for b in results.get('broadcasts', [])]
        results = self.api.top_live_status(broadcast_ids)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('broadcast_status_items', [])), 0, 'No broadcast_status_items returned.')

        results = self.api.top_live_status(str(broadcast_ids[0]))
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('broadcast_status_items', [])), 0, 'No broadcast_status_items returned.')

    def test_user_broadcast(self):
        broadcast = self.api.user_broadcast('25025320')     # Instagram
        self.assertIsNone(broadcast)

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

    @mock.patch('instagram_private_api.Client._call_api')
    def test_broadcast_like_mock(self, call_api):
        broadcast_id = 123
        call_api.return_value = {'status': 'ok'}

        like_count = 2
        params = {'user_like_count': str(like_count)}
        params.update(self.api.authenticated_params)
        self.api.broadcast_like(broadcast_id, like_count)
        call_api.assert_called_with(
            'live/%(broadcast_id)s/like/' % {'broadcast_id': broadcast_id},
            params=params)

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

    @mock.patch('instagram_private_api.Client._call_api')
    def test_broadcast_comment_mock(self, call_api):
        broadcast_id = 123
        call_api.return_value = {'status': 'ok'}

        comment_text = '<3'
        breadcrumb = gen_user_breadcrumb(len(comment_text))
        generated_uuid = self.api.generate_uuid()
        with mock.patch('instagram_private_api.endpoints.live.gen_user_breadcrumb') as gen_user_breadcrumb_mock, \
                mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock:
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
                'live/%(broadcast_id)s/comment/' % {'broadcast_id': broadcast_id},
                params=params)

    @unittest.skip('Modifies data.')
    def test_comment_like(self):
        results = self.api.comment_like('17852927593096945')
        self.assertEqual(results.get('status'), 'ok')

    @mock.patch('instagram_private_api.Client._call_api')
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

    @mock.patch('instagram_private_api.Client._call_api')
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
    def test_edit_media(self):
        results = self.api.self_feed()
        items = results.get('items', [])
        results = self.api.edit_media(items[0]['id'], 'Hello')
        self.assertEqual(results.get('status'), 'ok')

    @mock.patch('instagram_private_api.Client._call_api')
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

    @mock.patch('instagram_private_api.Client._call_api')
    def test_delete_media_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        params = {'media_id': media_id}
        params.update(self.api.authenticated_params)
        self.api.delete_media(media_id)
        call_api.assert_called_with(
            'media/%(media_id)s/delete/' % {'media_id': media_id},
            params=params)

    @unittest.skip('Modifies data.')
    def test_post_like(self):
        results = self.api.post_like('1486470123929723160_25025320')
        self.assertEqual(results.get('status'), 'ok')

    @mock.patch('instagram_private_api.Client._call_api')
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

    @mock.patch('instagram_private_api.Client._call_api')
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

    @mock.patch('instagram_private_api.Client._call_api')
    def test_post_comment_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'comment': {'created_at': '1234567890', 'pk': 100000,
                        'user': {'pk': 123, 'username': 'x', 'full_name': 'X', 'profile_pic_url': 'x.jpg'}}}
        media_id = '123_123'
        comment_text = '<3'
        breadcrumb = gen_user_breadcrumb(len(comment_text))
        generated_uuid = self.api.generate_uuid()
        with mock.patch('instagram_private_api.endpoints.media.gen_user_breadcrumb') as gen_user_breadcrumb_mock, \
                mock.patch('instagram_private_api.Client.generate_uuid') as generate_uuid_mock:
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

    @mock.patch('instagram_private_api.Client._call_api')
    def test_delete_comment_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        media_id = '123_123'
        comment_id = '123456'
        self.api.delete_comment(media_id, comment_id)
        call_api.assert_called_with(
            'media/%(media_id)s/comment/%(comment_id)s/delete/'
            % {'media_id': media_id, 'comment_id': comment_id},
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_friendships_create(self):
        results = self.api.friendships_create('2958144170')
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(results.get('friendship_status', {}).get('following'), True)

    @mock.patch('instagram_private_api.Client._call_api')
    def test_friendships_create_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'friendship_status': {'following': True}}
        user_id = '2958144170'
        params = {'user_id': user_id, 'radio_type': self.api.radio_type}
        params.update(self.api.authenticated_params)
        self.api.friendships_create(user_id)
        call_api.assert_called_with(
            'friendships/create/%(user_id)s/' % {'user_id': user_id},
            params=params)

    @unittest.skip('Modifies data.')
    def test_friendships_destroy(self):
        results = self.api.friendships_destroy('2958144170')
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(results.get('friendship_status', {}).get('following'), False)

    @mock.patch('instagram_private_api.Client._call_api')
    def test_friendships_destroy_mock(self, call_api):
        call_api.return_value = {'status': 'ok', 'following': False}
        user_id = '2958144170'
        params = {'user_id': user_id, 'radio_type': self.api.radio_type}
        params.update(self.api.authenticated_params)
        self.api.friendships_destroy(user_id)
        call_api.assert_called_with(
            'friendships/destroy/%(user_id)s/' % {'user_id': user_id},
            params=params)

    @unittest.skip('Modifies data.')
    def test_save_photo(self):
        results = self.api.save_photo(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @mock.patch('instagram_private_api.Client._call_api')
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

    @mock.patch('instagram_private_api.Client._call_api')
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

    def test_saved_feed(self):
        results = self.api.saved_feed()
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_remove_profile_picture(self):
        results = self.api.remove_profile_picture()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @mock.patch('instagram_private_api.Client._call_api')
    def test_remove_profile_picture_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}
        self.api.remove_profile_picture()
        call_api.assert_called_with(
            'accounts/remove_profile_picture/',
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_set_account_public(self):
        results = self.api.set_account_public()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @mock.patch('instagram_private_api.Client._call_api')
    def test_set_account_public_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}
        self.api.set_account_public()
        call_api.assert_called_with(
            'accounts/set_public/',
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_set_account_private(self):
        results = self.api.set_account_private()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @mock.patch('instagram_private_api.Client._call_api')
    def test_set_account_private_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}
        self.api.set_account_private()
        call_api.assert_called_with(
            'accounts/set_private/',
            params=self.api.authenticated_params)

    @unittest.skip('Modifies data.')
    def test_change_profile_picture(self):
        sample_url = 'https://c2.staticflickr.com/8/7162/6461496097_fdb8d1f7cc_b.jpg'
        res = urlopen(sample_url)
        photo_data = res.read()
        results = self.api.change_profile_picture(photo_data)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @unittest.skip('Modifies data.')
    def test_post_photo(self):
        sample_url = 'https://c1.staticflickr.com/5/4103/5059663679_85a7ec3f63_b.jpg'
        res = urlopen(sample_url)
        photo_data = res.read()
        size = (1024, 683)
        results = self.api.post_photo(photo_data, size=size, caption='')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_video(self):
        # Reposting from https://www.instagram.com/p/BL5hkEHDyd5/
        media_id = '1367271575733086073_2958144170'
        res = self.api.media_info(media_id)
        media_info = res['items'][0]
        video_url = media_info['videos']['standard_resolution']['url']
        video_size = (media_info['videos']['standard_resolution']['width'],
                      media_info['videos']['standard_resolution']['height'])
        thumbnail_url = media_info['images']['standard_resolution']['url']
        video_res = urlopen(video_url)
        video_data = video_res.read()
        thumb_res = urlopen(thumbnail_url)
        thumb_data = thumb_res.read()
        duration = media_info['video_duration']
        results = self.api.post_video(video_data, video_size, duration, thumb_data, caption='<3')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_album(self):
        # Reposting from https://www.instagram.com/p/BL5hkEHDyd5/
        media_id = '1367271575733086073_2958144170'
        res = self.api.media_info(media_id)
        media_info = res['items'][0]
        video_url = media_info['videos']['standard_resolution']['url']
        video_size = (media_info['videos']['standard_resolution']['width'],
                      media_info['videos']['standard_resolution']['height'])
        thumbnail_url = media_info['images']['standard_resolution']['url']
        video_res = urlopen(video_url)
        video_data = video_res.read()
        thumb_res = urlopen(thumbnail_url)
        thumb_data = thumb_res.read()
        duration = media_info['video_duration']
        medias = [
            {
                'type': 'image', 'size': video_size, 'data': thumb_data
            },
            {
                'type': 'video', 'size': video_size, 'duration': duration,
                'thumbnail': thumb_data, 'data': video_data
            }
        ]
        results = self.api.post_album(medias, caption='Testing...')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_photo_story(self):
        sample_url = 'http://i.imgur.com/3QzazV2.jpg'
        res = urlopen(sample_url)
        photo_data = res.read()
        size = (1080, 1920)
        results = self.api.post_photo_story(photo_data, size)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data.')
    def test_post_video_story(self):
        # Reposting https://streamable.com/08ico
        video_info_res = urlopen('https://api.streamable.com/videos/08ico')
        video_info = json.loads(video_info_res.read().decode('utf8'))
        mp4_info = video_info['files']['mp4']

        video_url = ('https:' if mp4_info['url'].startswith('//') else '') + mp4_info['url']
        video_size = (mp4_info['width'], mp4_info['height'])
        thumbnail_url = ('https:' if video_info['thumbnail_url'].startswith('//') else '') + video_info['thumbnail_url']
        duration = mp4_info['duration']

        video_res = urlopen(video_url)
        video_data = video_res.read()
        thumb_res = urlopen(thumbnail_url)
        thumb_data = thumb_res.read()
        results = self.api.post_video_story(video_data, video_size, duration, thumb_data)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @unittest.skip('Modifies data. Needs info setup.')
    def test_usertag_self_remove(self):
        results = self.api.usertag_self_remove(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    @mock.patch('instagram_private_api.Client._call_api')
    def test_usertag_self_remove_mock(self, call_api):
        media_id = '123'
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
        self.api.usertag_self_remove(media_id)
        call_api.assert_called_with(
            'usertags/%(media_id)s/remove/' % {'media_id': media_id},
            params=self.api.authenticated_params)

    def test_user_map(self):
        results = self.api.user_map(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('geo_media'))

    @unittest.skip('Modifies data.')
    def test_friendships_block(self):
        results = self.api.friendships_block(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertTrue(results.get('blocking'))

    @mock.patch('instagram_private_api.Client._call_api')
    def test_friendships_block_mock(self, call_api):
        call_api.return_value = {'status': 'ok', 'blocking': True}
        user_id = '2958144170'
        params = {'user_id': user_id}
        params.update(self.api.authenticated_params)
        self.api.friendships_block(user_id)
        call_api.assert_called_with(
            'friendships/block/%(user_id)s/' % {'user_id': user_id},
            params=params)

    def test_feed_popular(self):
        results = self.api.feed_popular()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_discover_channels_home(self):
        results = self.api.discover_channels_home()
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    def test_discover_chaining(self):
        results = self.api.discover_chaining(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('users', [])), 0, 'No users returned.')

    def test_megaphone_log(self):
        results = self.api.megaphone_log()
        self.assertEqual(results.get('status'), 'ok')
        self.assertTrue(results.get('success'))

    def test_expose(self):
        results = self.api.expose()
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_edit_profile(self):
        user = self.api.current_user()['user']
        results = self.api.edit_profile(
            first_name=user['full_name'],
            biography=user['biography'] + ' <3',
            external_url=user['external_url'],
            email=user['email'],
            phone_number=user['phone_number'],
            gender=user['gender']
        )
        self.assertEqual(results.get('status'), 'ok')
        returned_user = results['user']
        self.assertEqual(returned_user['full_name'], user['full_name'])
        self.assertEqual(returned_user['biography'], user['biography'] + ' <3')
        self.assertEqual(returned_user['external_url'], user['external_url'])
        self.assertEqual(returned_user['email'], user['email'])
        self.assertEqual(returned_user['phone_number'], user['phone_number'])
        self.assertEqual(returned_user['gender'], user['gender'])

    @mock.patch('instagram_private_api.Client._call_api')
    def test_edit_profile_mock(self, call_api):
        call_api.return_value = {
            'status': 'ok',
            'user': {'pk': 123, 'biography': '', 'profile_pic_url': 'https://example.com/x.jpg', 'external_url': ''}}

        params = {
            'username': self.api.authenticated_user_name,
            'gender': 1,
            'phone_number': '',
            'first_name': '',
            'biography': '',
            'external_url': '',
            'email': 'john@example.com',
        }
        params.update(self.api.authenticated_params)
        self.api.edit_profile(
            first_name=params['first_name'],
            biography=params['biography'],
            external_url=params['external_url'],
            email=params['email'],
            phone_number=params['phone_number'],
            gender=params['gender']
        )
        call_api.assert_called_with(
            'accounts/edit_profile/',
            params=params)

    @unittest.skip('Modifies data.')
    def test_logout(self):
        results = self.api.logout()
        self.assertEqual(results.get('status'), 'ok')

    @mock.patch('instagram_private_api.Client._call_api')
    def test_logout_mock(self, call_api):
        call_api.return_value = {'status': 'ok'}
        self.api.logout()
        call_api.assert_called_with(
            'accounts/logout/',
            params={
                'phone_id': self.api.phone_id,
                '_csrftoken': self.api.csrftoken,
                'guid': self.api.uuid,
                'device_id': self.api.device_id,
                '_uuid': self.api.uuid
            },
            unsigned=True)

    def test_top_search(self):
        results = self.api.top_search('cats')
        self.assertEqual(results.get('status'), 'ok')

    def test_stickers(self):
        results = self.api.stickers(location={'lat': '40.7484445', 'lng': '-73.9878531', 'horizontalAccuracy': 5.8})
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('static_stickers'))

        self.assertRaises(ValueError, lambda: self.api.stickers('x'))
        self.assertRaises(ValueError, lambda: self.api.stickers(location={'x': 1}))

    def test_check_username(self):
        results = self.api.check_username('instagram')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('available'))
        self.assertIsNotNone(results.get('error'))
        self.assertIsNotNone(results.get('error_type'))

    @unittest.skip('Modifies data.')
    def test_create_collection(self):
        name = 'A Collection'
        results = self.api.create_collection(name)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('collection_id'))
        self.assertEqual(results.get('collection_name'), name)

    @mock.patch('instagram_private_api.Client._call_api')
    def test_create_collection_mock(self, call_api):
        name = 'A Collection'
        call_api.return_value = {
            'status': 'ok',
            'collection_id': 123, 'collection_name': name}

        params = {'name': name}
        params.update(self.api.authenticated_params)
        self.api.create_collection(name)
        call_api.assert_called_with(
            'collections/create/',
            params=params)

    @unittest.skip('Modifies data.')
    def test_edit_collection(self):
        results = self.api.list_collections()
        self.assertTrue(results.get('items'), 'No collections')

        first_collection_id = results['items'][0]['collection_id']
        results = self.api.edit_collection(first_collection_id, ['1495028858729943288_25025320'])
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('collection_id'))

    @mock.patch('instagram_private_api.Client._call_api')
    def test_edit_collection_mock(self, call_api):
        collection_id = 123
        call_api.return_value = {
            'status': 'ok',
            'collection_id': collection_id, 'collection_name': 'A Collection'}

        media_ids = ['1495028858729943288_25025320']
        params = {'added_media_ids': json.dumps(media_ids, separators=(',', ':'))}
        params.update(self.api.authenticated_params)

        self.api.edit_collection(collection_id, media_ids)
        call_api.assert_called_with(
            'collections/%(collection_id)s/edit/' % {'collection_id': collection_id},
            params=params)

    @unittest.skip('Modifies data.')
    def test_delete_collection(self):
        results = self.api.list_collections()
        self.assertTrue(results.get('items'), 'No collections')

        first_collection_id = results['items'][0]['collection_id']
        results = self.api.delete_collection(first_collection_id)
        self.assertEqual(results.get('status'), 'ok')

    @mock.patch('instagram_private_api.Client._call_api')
    def test_delete_collection_mock(self, call_api):
        collection_id = 123
        call_api.return_value = {'status': 'ok'}

        self.api.delete_collection(collection_id)
        call_api.assert_called_with(
            'collections/%(collection_id)s/delete/' % {'collection_id': collection_id},
            params=self.api.authenticated_params)

    def test_collection_feed(self):
        results = self.api.list_collections()
        self.assertTrue(results.get('items'), 'No collection')

        first_collection_id = results['items'][0]['collection_id']
        results = self.api.collection_feed(first_collection_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertEqual(str(results.get('collection_id', '')), first_collection_id)
        self.assertIsNotNone(results.get('items'))

    def test_validate_useragent(self):
        ua = 'Instagram 9.2.0 Android (22/5.1.1; 480dpi; 1080x1920; Xiaomi; Redmi Note 3; kenzo; qcom; en_GB)'
        results = Client.validate_useragent(ua)
        self.assertEqual(results['parsed_params']['brand'], 'Xiaomi')
        self.assertEqual(results['parsed_params']['device'], 'Redmi Note 3')
        self.assertEqual(results['parsed_params']['model'], 'kenzo')
        self.assertEqual(results['parsed_params']['resolution'], '1080x1920')
        self.assertEqual(results['parsed_params']['dpi'], '480dpi')
        self.assertEqual(results['parsed_params']['chipset'], 'qcom')
        self.assertEqual(results['parsed_params']['android_version'], 22)
        self.assertEqual(results['parsed_params']['android_release'], '5.1.1')
        self.assertEqual(results['parsed_params']['app_version'], '9.2.0')

    def test_validate_useragent2(self):
        ua = 'Instagram 9.2.0 Android (xx/5.1.1; 480dpi; 1080x1920; Xiaomi; Redmi Note 3; kenzo; qcom; en_GB)'
        with self.assertRaises(ValueError):
            Client.validate_useragent(ua)

    def test_generate_useragent(self):
        custom_device = {
            'manufacturer': 'Samsung',
            'model': 'maguro',
            'device': 'Galaxy Nexus',
            'android_release': '4.3',
            'android_version': 18,
            'dpi': '320dpi',
            'resolution': '720x1280',
            'chipset': 'qcom'
        }
        custom_ua = Client.generate_useragent(
            android_release=custom_device['android_release'],
            android_version=custom_device['android_version'],
            phone_manufacturer=custom_device['manufacturer'],
            phone_device=custom_device['device'],
            phone_model=custom_device['model'],
            phone_dpi=custom_device['dpi'],
            phone_resolution=custom_device['resolution'],
            phone_chipset=custom_device['chipset']
        )
        self.assertEqual(
            custom_ua,
            'Instagram %s Android (%s/%s; %s; %s; '
            '%s; %s; %s; %s; en_US)'
            % (
                Constants.APP_VERSION,
                custom_device['android_version'],
                custom_device['android_release'],
                custom_device['dpi'],
                custom_device['resolution'],
                custom_device['manufacturer'],
                custom_device['device'],
                custom_device['model'],
                custom_device['chipset'],
            )
        )

    # Compat Patch Tests
    def test_compat_media(self):
        self.api.auto_patch = False
        results = self.api.media_info(self.test_media_id)
        self.api.auto_patch = True
        media = results.get('items', [])[0]
        media_patched = copy.deepcopy(media)
        ClientCompatPatch.media(media_patched)

        self.assertIsNone(media.get('link'))
        self.assertIsNotNone(media_patched.get('link'))
        self.assertIsNone(media.get('created_time'))
        self.assertIsNotNone(media_patched.get('created_time'))
        self.assertIsNone(media.get('images'))
        self.assertIsNotNone(media_patched.get('images'))
        self.assertIsNone(media.get('type'))
        self.assertIsNotNone(media_patched.get('type'))
        self.assertIsNone(media.get('filter'))
        self.assertIsNotNone(media_patched.get('filter'))
        self.assertIsNone(media.get('user', {}).get('id'))
        self.assertIsNotNone(media_patched.get('user', {}).get('id'))
        self.assertIsNone(media.get('user', {}).get('profile_picture'))
        self.assertIsNotNone(media_patched.get('user', {}).get('profile_picture'))
        if media['caption']:
            self.assertIsNone(media.get('caption', {}).get('id'))
            self.assertIsNotNone(media_patched['caption']['id'])
            self.assertIsNone(media.get('caption', {}).get('from'))
            self.assertIsNotNone(media_patched['caption']['from'])

    def test_compat_comment(self):
        self.api.auto_patch = False
        results = self.api.media_comments(self.test_media_id)
        self.api.auto_patch = True
        self.assertGreater(len(results.get('comments', [])), 0, 'No items returned.')
        comment = results.get('comments', [{}])[0]
        comment_patched = copy.deepcopy(comment)
        ClientCompatPatch.comment(comment_patched)
        self.assertIsNone(comment.get('id'))
        self.assertIsNotNone(comment_patched.get('id'))
        self.assertIsNone(comment.get('created_time'))
        self.assertIsNotNone(comment_patched.get('created_time'))
        self.assertIsNone(comment.get('from'))
        self.assertIsNotNone(comment_patched.get('from'))

    def test_compat_user(self):
        self.api.auto_patch = False
        results = self.api.user_info(self.test_user_id)
        self.api.auto_patch = True
        user = results.get('user', {})
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.user(user_patched)
        self.assertIsNone(user.get('id'))
        self.assertIsNotNone(user_patched.get('id'))
        self.assertIsNone(user.get('bio'))
        self.assertIsNotNone(user_patched.get('bio'))
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))
        self.assertIsNone(user.get('website'))
        self.assertIsNotNone(user_patched.get('website'))

    def test_compat_user_list(self):
        self.api.auto_patch = False
        results = self.api.user_following(self.test_user_id)
        self.api.auto_patch = True
        user = results.get('users', [{}])[0]
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.list_user(user_patched)
        self.assertIsNone(user.get('id'))
        self.assertIsNotNone(user_patched.get('id'))
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))

    def test_cookiejar_dump(self):
        dump = self.api.cookie_jar.dump()
        self.assertIsNotNone(dump)

    def test_gen_user_breadcrumb(self):
        output = gen_user_breadcrumb(15)
        self.assertIsNotNone(output)

    def test_max_chunk_size_generator(self):
        chunk_data = 'abcdefghijklmnopqrstuvwxyz'
        chunk_size = 5
        chunk_count = 0
        for chunk_info, data in max_chunk_size_generator(chunk_size, chunk_data):
            chunk_count += 1
            self.assertIsNotNone(data, 'Empty chunk.')
            self.assertLessEqual(len(data), chunk_size, 'Chunk size is too big.')
            self.assertEqual(len(data), chunk_info.length, 'Chunk length is wrong.')
            self.assertEqual(chunk_info.is_first, chunk_count == 1)

    def test_max_chunk_count_generator(self):
        chunk_data = 'abcdefghijklmnopqrstuvwxyz'
        expected_chunk_count = 5
        chunk_count = 0
        for chunk_info, data in max_chunk_count_generator(expected_chunk_count, chunk_data):
            chunk_count += 1
            self.assertIsNotNone(data, 'Empty chunk.')
            self.assertEqual(len(data), chunk_info.length, 'Chunk length is wrong.')
            self.assertEqual(chunk_info.is_first, chunk_count == 1)
            self.assertEqual(chunk_info.is_last, chunk_count == expected_chunk_count)

        self.assertEqual(chunk_count, expected_chunk_count, 'Chunk count is wrong.')

    def test_settings(self):
        results = self.api.settings
        for k in ('uuid', 'device_id', 'ad_id', 'signature_key', 'key_version',
                  'ig_capabilities', 'app_version', 'android_release', 'android_version',
                  'phone_manufacturer', 'phone_device', 'phone_model', 'phone_dpi', 'phone_resolution',
                  'phone_chipset', 'cookie', 'created_ts'):
            self.assertIsNotNone(results.get(k))

    def test_user_agent(self):
        ua = self.api.user_agent
        self.assertIsNotNone(ua)
        self.api.user_agent = ua

        def test_ua_setter():
            self.api.user_agent = 'Agent X'
        self.assertRaises(ValueError, test_ua_setter)

        custom_ua = self.api.generate_useragent(phone_manufacturer='BrandX')
        self.assertTrue('BrandX' in custom_ua)

        results = self.api.validate_useragent(custom_ua)
        self.assertEqual(results['parsed_params']['brand'], 'BrandX')

    def test_client_properties(self):
        results = self.api.get_cookie_value('non-existent-cookie-value')
        self.assertIsNone(results)

        self.assertIsNotNone(self.api.csrftoken)
        self.assertIsNotNone(self.api.token)
        self.assertIsNotNone(self.api.authenticated_user_id)
        self.assertIsNotNone(self.api.authenticated_user_name)
        self.assertIsNotNone(self.api.rank_token)
        self.assertIsNotNone(self.api.phone_id)
        self.assertIsNotNone(self.api.radio_type)
        self.assertIsNotNone(self.api.generate_deviceid())
        self.assertIsInstance(self.api.timezone_offset, int)


class TestPrivateApiUtils(unittest.TestCase):

    def __init__(self, testname):
        super(TestPrivateApiUtils, self).__init__(testname)

    def test_expand_code(self):
        id = InstagramID.expand_code('BRo7njqD75U')
        self.assertEqual(id, 1470687481426853460)

    def test_shorten_id(self):
        shortcode = InstagramID.shorten_id(1470687481426853460)
        self.assertEqual(shortcode, 'BRo7njqD75U')

    def test_shorten_media_id(self):
        shortcode = InstagramID.shorten_media_id('1470654893538426156_25025320')
        self.assertEqual(shortcode, 'BRo0NV0jD0s')

    def test_weblink_from_media_id(self):
        weblink = InstagramID.weblink_from_media_id('1470517649007430315_25025320')
        self.assertEqual(weblink, 'https://www.instagram.com/p/BRoVAK5B8qr/')


if __name__ == '__main__':

    warnings.simplefilter('ignore', UserWarning)
    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    #   python test_private_api.py -u "xxx" -p "xxx" -settings "saved_auth.json" -save

    parser = argparse.ArgumentParser(description='Test instagram_private_api.py')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-d', '--device_id', dest='device_id', type=str)
    parser.add_argument('-uu', '--uuid', dest='uuid', type=str)
    parser.add_argument('-save', '--save', action='store_true')
    parser.add_argument('-tests', '--tests', nargs='+')
    parser.add_argument('-debug', '--debug', action='store_true')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    print('Client version: %s' % __version__)

    cached_auth = None
    if args.settings_file_path and os.path.isfile(args.settings_file_path):
        with open(args.settings_file_path) as file_data:
            cached_auth = json.load(file_data)

    api = None
    if not cached_auth:

        ts_seed = str(int(os.path.getmtime(__file__)))
        if not args.uuid:
            # Example of how to generate a uuid.
            # You can generate a fixed uuid if you use a fixed value seed
            uuid = Client.generate_uuid(
                seed='%(pw)s.%(usr)s.%(ts)s' % {'pw': args.username, 'usr': args.password, 'ts': ts_seed})
        else:
            uuid = args.uuid

        if not args.device_id:
            # Example of how to generate a device id.
            # You can generate a fixed device id if you use a fixed value seed
            device_id = Client.generate_deviceid(
                seed='%(usr)s.%(ts)s.%(pw)s' % {'pw': args.password, 'usr': args.username, 'ts': ts_seed})
        else:
            device_id = args.device_id

        # Optional. You can custom the device settings instead of using the default one
        my_custom_device = {
            'manufacturer': 'Samsung',
            'model': 'maguro',
            'device': 'Galaxy Nexus',
            'android_release': '4.3',
            'android_version': 18,
            'dpi': '320dpi',
            'resolution': '720x1280',
            'chipset': 'qcom'
        }

        # start afresh without existing auth
        try:
            api = Client(
                args.username, args.password,
                auto_patch=True, drop_incompat_keys=False,
                guid=uuid, device_id=device_id,
                # custom device settings
                android_release=my_custom_device['android_release'],
                android_version=my_custom_device['android_version'],
                phone_manufacturer=my_custom_device['manufacturer'],
                phone_device=my_custom_device['device'],
                phone_model=my_custom_device['model'],
                phone_dpi=my_custom_device['dpi'],
                phone_resolution=my_custom_device['resolution'],
                phone_chipset=my_custom_device['chipset'])

        except ClientLoginError:
            print('Login Error. Please check your username and password.')
            sys.exit(99)

        # stuff that you should cache
        cached_auth = api.settings
        if args.save:
            # this auth cache can be re-used for up to 90 days
            with open(args.settings_file_path, 'w') as outfile:
                json.dump(cached_auth, outfile)

    else:
        try:
            # remove previous app version specific info so that we
            # can test the new sig key whenever there's an update
            for k in ['app_version', 'signature_key', 'key_version', 'ig_capabilities']:
                cached_auth.pop(k, None)
            api = Client(
                args.username, args.password,
                auto_patch=True, drop_incompat_keys=False,
                settings=cached_auth)

        except ClientCookieExpiredError:
            print('Cookie Expired. Please discard cached auth and login again.')
            sys.exit(99)

    tests = [
        {
            'name': 'test_login',
            'test': TestPrivateApi('test_login', api)
        },
        {
            'name': 'test_login_mock',
            'test': TestPrivateApi('test_login_mock', api)
        },
        {
            'name': 'test_login_failcsrf_mock',
            'test': TestPrivateApi('test_login_failcsrf_mock', api)
        },
        {
            'name': 'test_login_fail_mock',
            'test': TestPrivateApi('test_login_fail_mock', api)
        },
        {
            'name': 'test_sync',
            'test': TestPrivateApi('test_sync', api)
        },
        {
            'name': 'test_current_user',
            'test': TestPrivateApi('test_current_user', api)
        },
        {
            'name': 'test_autocomplete_user_list',
            'test': TestPrivateApi('test_autocomplete_user_list', api)
        },
        {
            'name': 'test_explore',
            'test': TestPrivateApi('test_explore', api)
        },
        {
            'name': 'test_ranked_recipients',
            'test': TestPrivateApi('test_ranked_recipients', api)
        },
        {
            'name': 'test_recent_recipients',
            'test': TestPrivateApi('test_recent_recipients', api)
        },
        {
            'name': 'test_news',
            'test': TestPrivateApi('test_news', api)
        },
        {
            'name': 'test_news_inbox',
            'test': TestPrivateApi('test_news_inbox', api)
        },
        {
            'name': 'test_direct_v2_inbox',
            'test': TestPrivateApi('test_direct_v2_inbox', api)
        },
        {
            'name': 'test_feed_liked',
            'test': TestPrivateApi('test_feed_liked', api)
        },
        {
            'name': 'test_user_info',
            'test': TestPrivateApi('test_user_info', api, user_id='124317')
        },
        {
            'name': 'test_user_info',
            'test': TestPrivateApi('test_user_info', api, user_id='322244991')
        },
        {
            'name': 'test_username_info',
            'test': TestPrivateApi('test_username_info', api, user_id='maruhanamogu')
        },
        {
            'name': 'test_user_detail_info',
            'test': TestPrivateApi('test_user_detail_info', api, user_id='124317')
        },
        {
            'name': 'test_feed_timeline',
            'test': TestPrivateApi('test_feed_timeline', api)
        },
        {
            'name': 'test_media_info',
            'test': TestPrivateApi('test_media_info', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_medias_info',
            'test': TestPrivateApi('test_medias_info', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_media_permalink',
            'test': TestPrivateApi('test_media_permalink', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_deleted_media_info',
            'test': TestPrivateApi('test_deleted_media_info', api, media_id='1291110080498251995_329452045')
        },
        {
            'name': 'test_media_comments',
            'test': TestPrivateApi('test_media_comments', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_deleted_media_comments',
            'test': TestPrivateApi('test_deleted_media_comments', api, media_id='1291110080498251995_329452045')
        },
        {
            'name': 'test_media_n_comments',
            'test': TestPrivateApi('test_media_n_comments', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_media_likers',
            'test': TestPrivateApi('test_media_likers', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_media_likers_chrono',
            'test': TestPrivateApi('test_media_likers_chrono', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_self_feed',
            'test': TestPrivateApi('test_self_feed', api)
        },
        {
            'name': 'test_user_feed',
            'test': TestPrivateApi('test_user_feed', api, user_id='124317')
        },
        {
            'name': 'test_username_feed',
            'test': TestPrivateApi('test_username_feed', api, user_id='maruhanamogu')
        },
        {
            'name': 'test_private_user_feed',
            'test': TestPrivateApi('test_private_user_feed', api, user_id='322244991')
        },
        {
            'name': 'test_user_following',
            'test': TestPrivateApi('test_user_following', api, user_id='124317')
        },
        {
            'name': 'test_user_followers',
            'test': TestPrivateApi('test_user_followers', api, user_id='124317')
        },
        {
            'name': 'test_search_users',
            'test': TestPrivateApi('test_search_users', api)
        },
        {
            'name': 'test_oembed',
            'test': TestPrivateApi('test_oembed', api)
        },
        {
            'name': 'test_reels_tray',
            'test': TestPrivateApi('test_reels_tray', api)
        },
        {
            'name': 'test_user_reel_media',
            'test': TestPrivateApi('test_user_reel_media', api, user_id='329452045')
        },
        {
            'name': 'test_reels_media',
            'test': TestPrivateApi('test_reels_media', api, user_id='329452045')
        },
        {
            'name': 'test_user_story_feed',
            'test': TestPrivateApi('test_user_story_feed', api, user_id='329452045')
        },
        {
            'name': 'test_friendships_show',
            'test': TestPrivateApi('test_friendships_show', api, user_id='329452045')
        },
        {
            'name': 'test_friendships_show_many',
            'test': TestPrivateApi('test_friendships_show_many', api, user_id=['329452045', '124317'])
        },
        {
            'name': 'test_friendships_pending',
            'test': TestPrivateApi('test_friendships_pending', api)
        },
        {
            'name': 'test_bulk_translate',
            'test': TestPrivateApi('test_bulk_translate', api)
        },
        {
            'name': 'test_translate',
            'test': TestPrivateApi('test_translate', api)
        },
        {
            'name': 'test_feed_tag',
            'test': TestPrivateApi('test_feed_tag', api)
        },
        {
            'name': 'test_tag_info',
            'test': TestPrivateApi('test_tag_info', api)
        },
        {
            'name': 'test_tag_related',
            'test': TestPrivateApi('test_tag_related', api)
        },
        {
            'name': 'test_tag_search',
            'test': TestPrivateApi('test_tag_search', api)
        },
        {
            'name': 'test_usertag_feed',
            'test': TestPrivateApi('test_usertag_feed', api, user_id='329452045')
        },
        {
            'name': 'test_location_feed',
            'test': TestPrivateApi('test_location_feed', api)
        },
        {
            'name': 'test_location_info',
            'test': TestPrivateApi('test_location_info', api)
        },
        {
            'name': 'test_location_related',
            'test': TestPrivateApi('test_location_related', api)
        },
        {
            'name': 'test_location_search',
            'test': TestPrivateApi('test_location_search', api)
        },
        {
            'name': 'test_location_fb_search',
            'test': TestPrivateApi('test_location_fb_search', api)
        },
        {
            'name': 'test_discover_top_live',
            'test': TestPrivateApi('test_discover_top_live', api)
        },
        {
            'name': 'test_suggested_broadcasts',
            'test': TestPrivateApi('test_suggested_broadcasts', api)
        },
        {
            'name': 'test_top_live_status',
            'test': TestPrivateApi('test_top_live_status', api)
        },
        {
            'name': 'test_user_broadcast',
            'test': TestPrivateApi('test_user_broadcast', api)
        },
        {
            'name': 'test_broadcast_info',
            'test': TestPrivateApi('test_broadcast_info', api)
        },
        {
            'name': 'test_broadcast_comments',
            'test': TestPrivateApi('test_broadcast_comments', api)
        },
        {
            'name': 'test_broadcast_heartbeat_and_viewercount',
            'test': TestPrivateApi('test_broadcast_heartbeat_and_viewercount', api)
        },
        {
            'name': 'test_broadcast_like_count',
            'test': TestPrivateApi('test_broadcast_like_count', api)
        },
        {
            'name': 'test_broadcast_like',
            'test': TestPrivateApi('test_broadcast_like', api)
        },
        {
            'name': 'test_broadcast_like_mock',
            'test': TestPrivateApi('test_broadcast_like_mock', api)
        },
        {
            'name': 'test_broadcast_comment',
            'test': TestPrivateApi('test_broadcast_comment', api)
        },
        {
            'name': 'test_broadcast_comment_mock',
            'test': TestPrivateApi('test_broadcast_comment_mock', api)
        },
        {
            'name': 'test_comment_like',
            'test': TestPrivateApi('test_comment_like', api)
        },
        {
            'name': 'test_comment_like_mock',
            'test': TestPrivateApi('test_comment_like_mock', api)
        },
        {
            'name': 'test_comment_unlike',
            'test': TestPrivateApi('test_comment_unlike', api)
        },
        {
            'name': 'test_comment_unlike_mock',
            'test': TestPrivateApi('test_comment_unlike_mock', api)
        },
        {
            'name': 'test_comment_likers',
            'test': TestPrivateApi('test_comment_likers', api)
        },
        {
            'name': 'test_edit_media',
            'test': TestPrivateApi('test_edit_media', api)
        },
        {
            'name': 'test_edit_media_mock',
            'test': TestPrivateApi('test_edit_media_mock', api)
        },
        {
            'name': 'test_delete_media',
            'test': TestPrivateApi('test_delete_media', api)
        },
        {
            'name': 'test_delete_media_mock',
            'test': TestPrivateApi('test_delete_media_mock', api)
        },
        {
            'name': 'test_post_like',
            'test': TestPrivateApi('test_post_like', api)
        },
        {
            'name': 'test_post_like_mock',
            'test': TestPrivateApi('test_post_like_mock', api)
        },
        {
            'name': 'test_delete_like',
            'test': TestPrivateApi('test_delete_like', api)
        },
        {
            'name': 'test_delete_like_mock',
            'test': TestPrivateApi('test_delete_like_mock', api)
        },
        {
            'name': 'test_post_comment_mock',
            'test': TestPrivateApi('test_post_comment_mock', api)
        },
        {
            'name': 'test_delete_comment_mock',
            'test': TestPrivateApi('test_delete_comment_mock', api)
        },
        {
            'name': 'test_friendships_create',
            'test': TestPrivateApi('test_friendships_create', api)
        },
        {
            'name': 'test_friendships_create_mock',
            'test': TestPrivateApi('test_friendships_create_mock', api)
        },
        {
            'name': 'test_friendships_destroy',
            'test': TestPrivateApi('test_friendships_destroy', api)
        },
        {
            'name': 'test_friendships_destroy_mock',
            'test': TestPrivateApi('test_friendships_destroy_mock', api)
        },
        {
            'name': 'test_save_photo',
            'test': TestPrivateApi('test_save_photo', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_save_photo_mock',
            'test': TestPrivateApi('test_save_photo_mock', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_unsave_photo',
            'test': TestPrivateApi('test_unsave_photo', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_unsave_photo_mock',
            'test': TestPrivateApi('test_unsave_photo_mock', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_saved_feed',
            'test': TestPrivateApi('test_saved_feed', api)
        },
        {
            'name': 'test_remove_profile_picture',
            'test': TestPrivateApi('test_remove_profile_picture', api)
        },
        {
            'name': 'test_remove_profile_picture_mock',
            'test': TestPrivateApi('test_remove_profile_picture_mock', api)
        },
        {
            'name': 'test_set_account_public',
            'test': TestPrivateApi('test_set_account_public', api)
        },
        {
            'name': 'test_set_account_public_mock',
            'test': TestPrivateApi('test_set_account_public_mock', api)
        },
        {
            'name': 'test_set_account_private',
            'test': TestPrivateApi('test_set_account_private', api)
        },
        {
            'name': 'test_set_account_private_mock',
            'test': TestPrivateApi('test_set_account_private_mock', api)
        },
        {
            'name': 'test_change_profile_picture',
            'test': TestPrivateApi('test_change_profile_picture', api)
        },
        {
            'name': 'test_post_photo',
            'test': TestPrivateApi('test_post_photo', api)
        },
        {
            'name': 'test_post_video',
            'test': TestPrivateApi('test_post_video', api)
        },
        {
            'name': 'test_post_album',
            'test': TestPrivateApi('test_post_album', api)
        },
        {
            'name': 'test_post_photo_story',
            'test': TestPrivateApi('test_post_photo_story', api)
        },
        {
            'name': 'test_post_video_story',
            'test': TestPrivateApi('test_post_video_story', api)
        },
        {
            'name': 'test_usertag_self_remove',
            'test': TestPrivateApi('test_usertag_self_remove', api, media_id='???')
        },
        {
            'name': 'test_usertag_self_remove_mock',
            'test': TestPrivateApi('test_usertag_self_remove_mock', api, media_id='???')
        },
        {
            'name': 'test_user_map',
            'test': TestPrivateApi('test_user_map', api, user_id='2958144170')
        },
        {
            'name': 'test_friendships_block',
            'test': TestPrivateApi('test_friendships_block', api, user_id='2958144170')
        },
        {
            'name': 'test_friendships_block_mock',
            'test': TestPrivateApi('test_friendships_block_mock', api, user_id='2958144170')
        },
        {
            'name': 'test_feed_popular',
            'test': TestPrivateApi('test_feed_popular', api)
        },
        {
            'name': 'test_discover_channels_home',
            'test': TestPrivateApi('test_discover_channels_home', api)
        },
        {
            'name': 'test_discover_chaining',
            'test': TestPrivateApi('test_discover_chaining', api, user_id='329452045')
        },
        {
            'name': 'test_megaphone_log',
            'test': TestPrivateApi('test_megaphone_log', api)
        },
        {
            'name': 'test_expose',
            'test': TestPrivateApi('test_expose', api)
        },
        {
            'name': 'test_edit_profile',
            'test': TestPrivateApi('test_edit_profile', api)
        },
        {
            'name': 'test_edit_profile_mock',
            'test': TestPrivateApi('test_edit_profile_mock', api)
        },
        {
            'name': 'test_logout',
            'test': TestPrivateApi('test_logout', api)
        },
        {
            'name': 'test_logout_mock',
            'test': TestPrivateApi('test_logout_mock', api)
        },
        {
            'name': 'test_top_search',
            'test': TestPrivateApi('test_top_search', api)
        },
        {
            'name': 'test_stickers',
            'test': TestPrivateApi('test_stickers', api)
        },
        {
            'name': 'test_check_username',
            'test': TestPrivateApi('test_check_username', api)
        },
        {
            'name': 'test_create_collection',
            'test': TestPrivateApi('test_create_collection', api)
        },
        {
            'name': 'test_create_collection_mock',
            'test': TestPrivateApi('test_create_collection_mock', api)
        },
        {
            'name': 'test_collection_feed',
            'test': TestPrivateApi('test_collection_feed', api)
        },
        {
            'name': 'test_edit_collection',
            'test': TestPrivateApi('test_edit_collection', api)
        },
        {
            'name': 'test_edit_collection_mock',
            'test': TestPrivateApi('test_edit_collection_mock', api)
        },
        {
            'name': 'test_delete_collection',
            'test': TestPrivateApi('test_delete_collection', api)
        },
        {
            'name': 'test_delete_collection_mock',
            'test': TestPrivateApi('test_delete_collection_mock', api)
        },
        {
            'name': 'test_validate_useragent',
            'test': TestPrivateApi('test_validate_useragent', api)
        },
        {
            'name': 'test_validate_useragent2',
            'test': TestPrivateApi('test_validate_useragent2', api)
        },
        {
            'name': 'test_generate_useragent',
            'test': TestPrivateApi('test_generate_useragent', api)
        },
        {
            'name': 'test_compat_media',
            'test': TestPrivateApi('test_compat_media', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_compat_comment',
            'test': TestPrivateApi('test_compat_comment', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_compat_user',
            'test': TestPrivateApi('test_compat_user', api, user_id='124317')
        },
        {
            'name': 'test_compat_user_list',
            'test': TestPrivateApi('test_compat_user_list', api, user_id='124317')
        },
        {
            'name': 'test_cookiejar_dump',
            'test': TestPrivateApi('test_cookiejar_dump', api)
        },
        {
            'name': 'test_gen_user_breadcrumb',
            'test': TestPrivateApi('test_gen_user_breadcrumb', api)
        },
        {
            'name': 'test_max_chunk_size_generator',
            'test': TestPrivateApi('test_max_chunk_size_generator', api)
        },
        {
            'name': 'test_max_chunk_count_generator',
            'test': TestPrivateApi('test_max_chunk_count_generator', api)
        },
        {
            'name': 'test_settings',
            'test': TestPrivateApi('test_settings', api)
        },
        {
            'name': 'test_user_agent',
            'test': TestPrivateApi('test_user_agent', api)
        },
        {
            'name': 'test_client_properties',
            'test': TestPrivateApi('test_client_properties', api)
        },
        {
            'name': 'test_expand_code',
            'test': TestPrivateApiUtils('test_expand_code')
        },
        {
            'name': 'test_shorten_id',
            'test': TestPrivateApiUtils('test_shorten_id')
        },
        {
            'name': 'test_shorten_media_id',
            'test': TestPrivateApiUtils('test_shorten_media_id')
        },
        {
            'name': 'test_weblink_from_media_id',
            'test': TestPrivateApiUtils('test_weblink_from_media_id')
        },
    ]

    def match_regex(test_name):
        for test_re in args.tests:
            test_re = r'%s' % test_re
            if re.match(test_re, test_name):
                return True
        return False

    if args.tests:
        tests = filter(lambda x: match_regex(x['name']), tests)

    try:
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(test['test'])
        unittest.TextTestRunner(verbosity=2).run(suite)

    except ClientError as e:
        print('Unexpected ClientError %s (Code: %d, Response: %s)' % (e.msg, e.code, e.error_response))
