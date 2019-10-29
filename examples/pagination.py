import json
import os.path
import logging
import argparse
try:
    from instagram_private_api import (
        Client, __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, __version__ as client_version)


if __name__ == '__main__':

    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    # python examples/savesettings_logincallback.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    parser = argparse.ArgumentParser(description='Pagination demo')
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-debug', '--debug', action='store_true')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    print('Client version: {0!s}'.format(client_version))
    api = Client(args.username, args.password)

    # ---------- Pagination with max_id ----------
    user_id = '2958144170'
    updates = []
    results = api.user_feed(user_id)
    updates.extend(results.get('items', []))

    next_max_id = results.get('next_max_id')
    while next_max_id:
        results = api.user_feed(user_id, max_id=next_max_id)
        updates.extend(results.get('items', []))
        if len(updates) >= 30:       # get only first 30 or so
            break
        next_max_id = results.get('next_max_id')

    updates.sort(key=lambda x: x['pk'])
    # print list of IDs
    print(json.dumps([u['pk'] for u in updates], indent=2))

    # ---------- Pagination with rank_token and exclusion list ----------
    rank_token = Client.generate_uuid()
    has_more = True
    tag_results = []
    while has_more and rank_token and len(tag_results) < 60:
        results = api.tag_search(
            'cats', rank_token, exclude_list=[t['id'] for t in tag_results])
        tag_results.extend(results.get('results', []))
        has_more = results.get('has_more')
        rank_token = results.get('rank_token')
    print(json.dumps([t['name'] for t in tag_results], indent=2))
