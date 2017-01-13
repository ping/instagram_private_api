import json
import datetime
import os.path
import logging
import argparse
try:
    import instagram_private_api as app_api
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import instagram_private_api as app_api


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, indent=2)
        print('SAVED: %s' % new_settings_file)


if __name__ == '__main__':

    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    # python examples/savesettings_logincallback.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    parser = argparse.ArgumentParser(description='Pagination demo')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-debug', '--debug', action='store_true')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    print('Client version: %s' % app_api.__version__)

    try:

        settings_file = args.settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('Unable to find file: %s' % settings_file)

            # login new
            api = app_api.Client(
                args.username, args.password,
                auto_patch=True, drop_incompat_keys=False,
                on_login=lambda x: onlogin_callback(x, args.settings_file_path))
        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data)
            print('Reusing settings: %s' % settings_file)

            # reuse auth settings
            api = app_api.Client(
                args.username, args.password,
                auto_patch=True, drop_incompat_keys=False,
                settings=cached_settings)

    except app_api.ClientCookieExpiredError as e:
        print('ClientCookieExpiredError: %s' % e)

        # Login expired
        # Do relogin but use default ua, keys and such
        api = app_api.Client(
            args.username, args.password,
            auto_patch=True, drop_incompat_keys=False,
            on_login=lambda x: onlogin_callback(x, args.settings_file_path))

    except app_api.ClientLoginError as e:
        print ('ClientLoginError %s' % e)
        exit(9)
    except app_api.ClientError as e:
        print ('ClientError %s (Code: %d, Response: %s)' % (e.msg, e.code, e.error_response))
        exit(9)
    except Exception as e:
        print('Unexpected Exception: %s' % e)
        exit(99)

    # Call the api
    user_id = '2958144170'
    followers = []
    results = api.user_followers(user_id)
    followers.extend(results.get('users', []))

    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = api.user_followers(user_id, max_id=next_max_id)
        followers.extend(results.get('users', []))
        if len(followers) >= 600:       # get only first 600 or so
            break
        next_max_id = results.get('next_max_id')

    followers.sort(key=lambda x: x['pk'])
    # print list of user IDs
    print(json.dumps([u['pk'] for u in followers], indent=2))
