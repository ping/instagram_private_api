import unittest
import argparse
import os
import json
import sys
import logging
import re
import warnings

from .private import (
    AccountTests, CollectionsTests, DiscoverTests,
    FeedTests, FriendshipTests, LiveTests,
    LocationTests, MediaTests, MiscTests,
    TagsTests, UploadTests, UsersTests,
    UsertagsTests, HighlightsTests,
    ClientTests, ApiUtilsTests, CompatPatchTests,
    IGTVTests,
)
from .common import (
    Client, ClientError, ClientLoginError, ClientCookieExpiredError,
    __version__, to_json, from_json
)


if __name__ == '__main__':

    warnings.simplefilter('ignore', UserWarning)
    logging.basicConfig(format='%(name)s %(message)s', stream=sys.stdout)
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

    print('Client version: {0!s}'.format(__version__))

    cached_auth = None
    if args.settings_file_path and os.path.isfile(args.settings_file_path):
        with open(args.settings_file_path) as file_data:
            cached_auth = json.load(file_data, object_hook=from_json)

    # Optional. You can custom the device settings instead of using the default one
    my_custom_device = {
        'phone_manufacturer': 'LGE/lge',
        'phone_model': 'RS988',
        'phone_device': 'h1',
        'android_release': '6.0.1',
        'android_version': 23,
        'phone_dpi': '640dpi',
        'phone_resolution': '1440x2392',
        'phone_chipset': 'h1'
    }

    api = None
    if not cached_auth:

        ts_seed = str(int(os.path.getmtime(__file__)))
        if not args.uuid:
            # Example of how to generate a uuid.
            # You can generate a fixed uuid if you use a fixed value seed
            uuid = Client.generate_uuid(
                seed='{pw!s}.{usr!s}.{ts!s}'.format(**{'pw': args.username, 'usr': args.password, 'ts': ts_seed}))
        else:
            uuid = args.uuid

        if not args.device_id:
            # Example of how to generate a device id.
            # You can generate a fixed device id if you use a fixed value seed
            device_id = Client.generate_deviceid(
                seed='{usr!s}.{ts!s}.{pw!s}'.format(**{'pw': args.password, 'usr': args.username, 'ts': ts_seed}))
        else:
            device_id = args.device_id

        # start afresh without existing auth
        try:
            api = Client(
                args.username, args.password,
                auto_patch=True, drop_incompat_keys=False,
                guid=uuid, device_id=device_id,
                # custom device settings
                **my_custom_device)

        except ClientLoginError:
            print('Login Error. Please check your username and password.')
            sys.exit(99)

        # stuff that you should cache
        cached_auth = api.settings
        if args.save:
            # this auth cache can be re-used for up to 90 days
            with open(args.settings_file_path, 'w') as outfile:
                json.dump(cached_auth, outfile, default=to_json)

    else:
        try:
            # remove previous app version specific info so that we
            # can test the new sig key whenever there's an update
            for k in ['app_version', 'signature_key', 'key_version', 'ig_capabilities']:
                cached_auth.pop(k, None)
            api = Client(
                args.username, args.password,
                auto_patch=True, drop_incompat_keys=False,
                settings=cached_auth,
                **my_custom_device)

        except ClientCookieExpiredError:
            print('Cookie Expired. Please discard cached auth and login again.')
            sys.exit(99)

    tests = []
    tests.extend(AccountTests.init_all(api))
    tests.extend(CollectionsTests.init_all(api))
    tests.extend(DiscoverTests.init_all(api))
    tests.extend(FeedTests.init_all(api))
    tests.extend(FriendshipTests.init_all(api))
    tests.extend(LiveTests.init_all(api))
    tests.extend(LocationTests.init_all(api))
    tests.extend(MediaTests.init_all(api))
    tests.extend(MiscTests.init_all(api))
    tests.extend(TagsTests.init_all(api))
    tests.extend(UploadTests.init_all(api))
    tests.extend(UsersTests.init_all(api))
    tests.extend(UsertagsTests.init_all(api))
    tests.extend(HighlightsTests.init_all(api))
    tests.extend(IGTVTests.init_all(api))

    tests.extend(ClientTests.init_all(api))
    tests.extend(CompatPatchTests.init_all(api))
    tests.extend(ApiUtilsTests.init_all())

    def match_regex(test_name):
        for test_re in args.tests:
            test_re = r'{0!s}'.format(test_re)
            if re.match(test_re, test_name):
                return True
        return False

    if args.tests:
        tests = filter(lambda x: match_regex(x['name']), tests)

    try:
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(test['test'])
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(not result.wasSuccessful())

    except ClientError as e:
        print('Unexpected ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(
            e.msg, e.code, e.error_response))
