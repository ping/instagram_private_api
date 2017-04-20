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
    from instagram_web_api import (
        __version__, Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientCompatPatch)
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_web_api import (
        __version__, Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientCompatPatch)


class TestWebApi(unittest.TestCase):

    def __init__(self, testname, api):
        super(TestWebApi, self).__init__(testname)
        self.api = api

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.test_user_id = '25025320'
        self.test_media_shortcode = 'BJL-gjsDyo1'
        self.test_media_id = '1009392755603152985'
        self.test_comment_id = '1234567890'

    def tearDown(self):
        time.sleep(2.5)   # sleep a bit between tests to avoid HTTP429 errors

    def test_user_info(self):
        results = self.api.user_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('profile_picture'))

    def test_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
        self.assertGreater(len(results), 0)

    def test_notfound_user_feed(self):
        self.assertRaises(ClientError, lambda: self.api.user_feed('1'))

    def test_user_feed_extract(self, extract=True):
        results = self.api.user_feed(self.test_user_id)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], dict)

    def test_media_info(self):
        results = self.api.media_info(self.test_media_shortcode)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('link'))
        self.assertIsNotNone(results.get('images'))

    def test_notfound_media_info(self):
        self.assertRaises(ClientError, lambda: self.api.media_info('BSgmaRDg-xX'))

    def test_carousel_media_info(self):
        results = self.api.media_info2('BQ0eAlwhDrw')
        self.assertIsNotNone(results.get('link'))
        self.assertIsNotNone(results.get('type'))
        self.assertIsNotNone(results.get('images'))

    def test_media_comments(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20)
        self.assertGreaterEqual(len(results), 0)

    def test_notfound_media_comments(self):
        self.assertRaises(ClientError, lambda: self.api.media_comments('BSgmaRDg-xX'))

    def test_media_comments_extract(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20, extract=True)
        self.assertGreaterEqual(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_user_followers(self):
        results = self.api.user_followers(self.test_user_id)
        self.assertGreater(len(results), 0)

    def test_user_followers_extract(self):
        results = self.api.user_followers(self.test_user_id, extract=True)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_user_following(self):
        results = self.api.user_following(self.test_user_id)
        self.assertGreater(len(results), 0)

    @unittest.skip('Modifies data.')
    def test_post_comment(self):
        results = self.api.post_comment(self.test_media_id, '<3')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('id'))

    @unittest.skip('Modifies data / Needs actual data.')
    def test_del_comment(self):
        results = self.api.delete_comment(self.test_media_id, self.test_comment_id)
        self.assertEqual(results.get('status'), 'ok')

    def test_search(self):
        results = self.api.search('maru')
        self.assertGreaterEqual(len(results['users']), 0)
        self.assertGreaterEqual(len(results['hashtags']), 0)

    def test_client_properties(self):
        self.assertIsNotNone(self.api.csrftoken)
        self.assertIsNotNone(self.api.authenticated_user_id)
        self.assertIsNone(self.api.authenticated_user_name)
        self.assertTrue(self.api.is_authenticated)
        settings = self.api.settings
        for k in ('user_agent', 'cookie', 'created_ts'):
            self.assertIsNotNone(settings.get(k))
        self.assertIsNotNone(self.api.cookie_jar.dump())

    # Compat Patch Tests
    def test_compat_media(self):
        self.api.auto_patch = False
        media = self.api.media_info(self.test_media_shortcode)
        media_patched = copy.deepcopy(media)
        ClientCompatPatch.media(media_patched)
        self.api.auto_patch = True
        self.assertIsNone(media.get('link'))
        self.assertIsNotNone(media_patched.get('link'))
        self.assertIsNone(media.get('user'))
        self.assertIsNotNone(media_patched.get('user'))
        self.assertIsNone(media.get('type'))
        self.assertIsNotNone(media_patched.get('type'))
        self.assertIsNone(media.get('images'))
        self.assertIsNotNone(media_patched.get('images'))
        self.assertIsNone(media.get('created_time'))
        self.assertIsNotNone(media_patched.get('created_time'))
        self.assertIsNotNone(re.match(r'\d+_\d+', media_patched['id']))

    def test_compat_comment(self):
        self.api.auto_patch = False
        comment = self.api.media_comments(self.test_media_shortcode, count=1)[0]
        comment_patched = copy.deepcopy(comment)
        self.api.auto_patch = True
        ClientCompatPatch.comment(comment_patched)
        self.assertIsNone(comment.get('created_time'))
        self.assertIsNotNone(comment_patched.get('created_time'))
        self.assertIsNone(comment.get('from'))
        self.assertIsNotNone(comment_patched.get('from'))

    def test_compat_user(self):
        self.api.auto_patch = False
        user = self.api.user_info(self.test_user_id)
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.user(user_patched)
        self.api.auto_patch = True
        self.assertIsNone(user.get('bio'))
        self.assertIsNotNone(user_patched.get('bio'))
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))
        self.assertIsNone(user.get('website'))
        self.assertIsNotNone(user_patched.get('website'))
        self.assertIsNone(user.get('counts'))
        self.assertIsNotNone(user_patched.get('counts'))

    def test_compat_user_list(self):
        self.api.auto_patch = False
        user = self.api.user_followers(self.test_user_id)[0]
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.list_user(user_patched)
        self.api.auto_patch = True
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))


if __name__ == '__main__':

    warnings.simplefilter('ignore', UserWarning)
    logging.basicConfig()
    logger = logging.getLogger('instagram_web_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    #   python test_web_api.py -u "xxx" -p "xxx" -save -settings "web_settings.json"

    parser = argparse.ArgumentParser(description='Test instagram_web_api.py')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-u', '--username', dest='username', type=str)
    parser.add_argument('-p', '--password', dest='password', type=str)
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
    if not cached_auth and args.username and args.password:
        # start afresh without existing auth
        try:
            print('New login.')
            api = Client(
                auto_patch=True, drop_incompat_keys=False,
                username=args.username, password=args.password, authenticate=True)
        except ClientLoginError:
            print('Login Error. Please check your username and password.')
            sys.exit(99)

        cached_auth = api.settings
        if args.save:
            # this auth cache can be re-used for up to 90 days
            with open(args.settings_file_path, 'w') as outfile:
                json.dump(cached_auth, outfile)

    elif cached_auth and args.username and args.password:
        try:
            print('Reuse login.')
            api = Client(
                auto_patch=True, drop_incompat_keys=False,
                username=args.username,
                password=args.password,
                settings=cached_auth)
        except ClientCookieExpiredError:
            print('Cookie Expired. Please discard cached auth and login again.')
            sys.exit(99)

    else:
        # unauthenticated client instance
        print('Unauthenticated.')
        api = Client(auto_patch=True, drop_incompat_keys=False)

    if not api:
        raise Exception('Unable to initialise api.')

    tests = [
        {
            'name': 'test_user_info',
            'test': TestWebApi('test_user_info', api),
        },
        {
            'name': 'test_user_feed',
            'test': TestWebApi('test_user_feed', api),
        },
        {
            'name': 'test_notfound_user_feed',
            'test': TestWebApi('test_notfound_user_feed', api)
        },
        {
            'name': 'test_user_feed_extract',
            'test': TestWebApi('test_user_feed_extract', api)
        },
        {
            'name': 'test_media_info',
            'test': TestWebApi('test_media_info', api),
        },
        {
            'name': 'test_notfound_media_info',
            'test': TestWebApi('test_notfound_media_info', api)
        },
        {
            'name': 'test_media_comments',
            'test': TestWebApi('test_media_comments', api),
        },
        {
            'name': 'test_notfound_media_comments',
            'test': TestWebApi('test_notfound_media_comments', api)
        },
        {
            'name': 'test_media_comments_extract',
            'test': TestWebApi('test_media_comments_extract', api)
        },
        {
            'name': 'test_search',
            'test': TestWebApi('test_search', api),
        },
        {
            'name': 'test_user_followers',
            'test': TestWebApi('test_user_followers', api),
            'require_auth': True,
        },
        {
            'name': 'test_user_followers_extract',
            'test': TestWebApi('test_user_followers_extract', api),
            'require_auth': True,
        },
        {
            'name': 'test_user_following',
            'test': TestWebApi('test_user_following', api),
            'require_auth': True,
        },
        {
            'name': 'test_post_comment',
            'test': TestWebApi('test_post_comment', api),
            'require_auth': True,
        },
        {
            'name': 'test_del_comment',
            'test': TestWebApi('test_del_comment', api),
            'require_auth': True,
        },
        {
            'name': 'test_compat_media',
            'test': TestWebApi('test_compat_media', api),
        },
        {
            'name': 'test_compat_comment',
            'test': TestWebApi('test_compat_comment', api),
        },
        {
            'name': 'test_compat_user',
            'test': TestWebApi('test_compat_user', api),
        },
        {
            'name': 'test_compat_user_list',
            'test': TestWebApi('test_compat_user_list', api),
            'require_auth': True,
        },
        {
            'name': 'test_carousel_media_info',
            'test': TestWebApi('test_carousel_media_info', api),
        },
        {
            'name': 'test_client_properties',
            'test': TestWebApi('test_client_properties', api),
            'require_auth': True,
        }
    ]

    suite = unittest.TestSuite()

    def match_regex(test_name):
        for test_re in args.tests:
            test_re = r'%s' % test_re
            if re.match(test_re, test_name):
                return True
        return False

    if args.tests:
        tests = filter(lambda x: match_regex(x['name']), tests)

    if not api.is_authenticated:
        tests = filter(lambda x: not x.get('require_auth', False), tests)

    for test in tests:
        suite.addTest(test['test'])

    try:
        unittest.TextTestRunner(verbosity=2).run(suite)
    except ClientError as e:
        print('Unexpected ClientError %s (Code: %d)' % (e.msg, e.code))
