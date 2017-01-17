import unittest
import argparse
import os
import time
import json
import sys
import logging
try:
    from instagram_web_api import __version__, Client, ClientError, ClientLoginError, ClientCookieExpiredError
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_web_api import __version__, Client, ClientError, ClientLoginError, ClientCookieExpiredError


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
        time.sleep(5)   # sleep a bit between tests to avoid HTTP429 errors

    def test_user_info(self):
        results = self.api.user_info(self.test_user_id)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('profile_picture'))

    def test_user_feed(self):
        results = self.api.user_feed(self.test_user_id)
        self.assertGreater(len(results), 0)

    def test_media_info(self):
        results = self.api.media_info(self.test_media_shortcode)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('link'))

    def test_media_comments(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20)
        self.assertGreaterEqual(len(results), 0)

    def test_user_followers(self):
        results = self.api.user_followers(self.test_user_id)
        self.assertGreater(len(results), 0)

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


if __name__ == '__main__':

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
            'name': 'test_media_info',
            'test': TestWebApi('test_media_info', api),
        },
        {
            'name': 'test_media_comments',
            'test': TestWebApi('test_media_comments', api),
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
            'name': 'test_user_following',
            'test': TestWebApi('test_user_followers', api),
            'require_auth': True,
        },
        {
            'name': 'test_post_comment',
            'test': TestWebApi('test_user_followers', api),
            'require_auth': True,
        },
        {
            'name': 'test_del_comment',
            'test': TestWebApi('test_user_followers', api),
            'require_auth': True,
        },
    ]

    suite = unittest.TestSuite()

    if args.tests:
        tests = filter(lambda x: x['name'] in args.tests, tests)

    if not api.is_authenticated:
        tests = filter(lambda x: not x.get('require_auth', False), tests)

    for test in tests:
        suite.addTest(test['test'])

    try:
        unittest.TextTestRunner(verbosity=2).run(suite)
    except ClientError as e:
        print('Unexpected ClientError %s (Code: %d)' % (e.msg, e.code))
