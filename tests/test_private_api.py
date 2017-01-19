import unittest
import argparse
import os
import time
import json
import sys
import logging
try:
    # python 2.x
    from urllib2 import urlopen, Request
except ImportError:
    # python 3.x
    from urllib.request import urlopen, Request     # noqa
try:
    from instagram_private_api import __version__, Client, ClientError, ClientLoginError, ClientCookieExpiredError
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import __version__, Client, ClientError, ClientLoginError, ClientCookieExpiredError


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
        time.sleep(5)   # sleep a bit between tests to avoid HTTP429 errors

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

    def test_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
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
        results = self.api.location_search('40.7484445', '-73.9878531')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('venues', [])), 0, 'No venues returned.')

    def test_location_fb_search(self):
        results = self.api.location_fb_search('Paris, France')
        self.assertEqual(results.get('status'), 'ok')
        self.assertGreater(len(results.get('items', [])), 0, 'No items returned.')

    @unittest.skip('Not available.')
    def test_discover_top_live(self):
        results = self.api.discover_top_live()
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_comment_like(self):
        results = self.api.comment_like('17852927593096945')
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_comment_unlike(self):
        results = self.api.comment_unlike('17852927593096945')
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_edit_media(self):
        results = self.api.edit_media(self.test_media_id, 'Hello')
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_delete_media(self):
        results = self.api.delete_media(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_save_photo(self):
        results = self.api.save_photo(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_unsave_photo(self):
        results = self.api.unsave_photo(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    def test_saved_feed(self):
        results = self.api.saved_feed()
        self.assertEqual(results.get('status'), 'ok')

    @unittest.skip('Modifies data.')
    def test_remove_profile_picture(self):
        results = self.api.remove_profile_picture()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @unittest.skip('Modifies data.')
    def test_set_account_public(self):
        results = self.api.set_account_public()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

    @unittest.skip('Modifies data.')
    def test_set_account_private(self):
        results = self.api.set_account_private()
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('user'))

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

    @unittest.skip('Modifies data. Needs info setup.')
    def test_usertag_self_remove(self):
        results = self.api.usertag_self_remove(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('media'))

    def test_user_map(self):
        results = self.api.user_map(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('geo_media'))

    @unittest.skip('Modifies data.')
    def test_friendships_block(self):
        results = self.api.friendships_block(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertTrue(results.get('blocking'))

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

    @unittest.skip('Modifies data.')
    def test_logout(self):
        results = self.api.logout()
        self.assertEqual(results.get('status'), 'ok')


if __name__ == '__main__':

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
            api = Client(
                args.username, args.password,
                auto_patch=True, drop_incompat_keys=False,
                settings=cached_auth)

        except ClientCookieExpiredError:
            print('Cookie Expired. Please discard cached auth and login again.')
            sys.exit(99)

    suite = unittest.TestSuite()
    tests = [
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
            'name': 'test_comment_like',
            'test': TestPrivateApi('test_comment_like', api)
        },
        {
            'name': 'test_comment_unlike',
            'test': TestPrivateApi('test_comment_unlike', api)
        },
        {
            'name': 'test_save_photo',
            'test': TestPrivateApi('test_save_photo', api, media_id='1206573574980690068_1497851591')
        },
        {
            'name': 'test_unsave_photo',
            'test': TestPrivateApi('test_unsave_photo', api, media_id='1206573574980690068_1497851591')
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
            'name': 'test_set_account_public',
            'test': TestPrivateApi('test_set_account_public', api)
        },
        {
            'name': 'test_set_account_private',
            'test': TestPrivateApi('test_set_account_private', api)
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
            'name': 'test_usertag_self_remove',
            'test': TestPrivateApi('test_usertag_self_remove', api, media_id='???')
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
            'name': 'test_logout',
            'test': TestPrivateApi('test_logout', api)
        }
    ]

    if args.tests:
        tests = filter(lambda x: x['name'] in args.tests, tests)
    for test in tests:
        suite.addTest(test['test'])

    try:
        unittest.TextTestRunner(verbosity=2).run(suite)
    except ClientError as e:
        print('Unexpected ClientError %s (Code: %d, Response: %s)' % (e.msg, e.code, e.error_response))
