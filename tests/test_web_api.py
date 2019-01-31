import unittest
import argparse
import os
import json
import sys
import logging
import re
import warnings

from .common import (
    __webversion__ as __version__,
    to_json, from_json,
    WebClient as Client,
    WebClientError as ClientError,
    WebClientLoginError as ClientLoginError,
    WebClientCookieExpiredError as ClientCookieExpiredError
)
from .web import (
    ClientTests, MediaTests, UserTests,
    CompatPatchTests, UploadTests,
    FeedTests, UnauthenticatedTests,
)

if __name__ == '__main__':

    warnings.simplefilter('ignore', UserWarning)
    logging.basicConfig(format='%(name)s %(message)s', stream=sys.stdout)
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

    print('Client version: {0!s}'.format(__version__))

    cached_auth = None
    if args.settings_file_path and os.path.isfile(args.settings_file_path):
        with open(args.settings_file_path) as file_data:
            cached_auth = json.load(file_data, object_hook=from_json)

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
                json.dump(cached_auth, outfile, default=to_json)

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

    tests = []
    tests.extend(ClientTests.init_all(api))
    tests.extend(MediaTests.init_all(api))
    tests.extend(UserTests.init_all(api))
    tests.extend(CompatPatchTests.init_all(api))
    tests.extend(UploadTests.init_all(api))
    tests.extend(FeedTests.init_all(api))
    web_api = Client(auto_patch=True, drop_incompat_keys=False)
    tests.extend(UnauthenticatedTests.init_all(web_api))

    def match_regex(test_name):
        for test_re in args.tests:
            test_re = r'{0!s}'.format(test_re)
            if re.match(test_re, test_name):
                return True
        return False

    if args.tests:
        tests = filter(lambda x: match_regex(x['name']), tests)

    if not api.is_authenticated:
        tests = filter(lambda x: not x.get('require_auth', False), tests)

    try:
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(test['test'])
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(not result.wasSuccessful())

    except ClientError as e:
        print('Unexpected ClientError {0!s} (Code: {1:d})'.format(e.msg, e.code))
