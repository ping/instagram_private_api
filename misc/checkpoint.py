import re
import gzip
from io import BytesIO
try:
    # python 2.x
    from urllib2 import urlopen, Request
    from urllib import urlencode, unquote_plus
except ImportError:
    # python 3.x
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode, unquote_plus

import sys


class Checkpoint:
    """OBSOLETE. No longer working or supported."""

    USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) ' \
                 'AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34 ' \
                 'Instagram 9.2.0 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334)'

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.csrftoken = ''
        self.cookie = ''
        self.endpoint = 'https://i.instagram.com/integrity/checkpoint/' \
                        'checkpoint_logged_out_main/%(user_id)s/?%(params)s' % \
                        {
                            'user_id': self.user_id,
                            'params': urlencode({'next': 'instagram://checkpoint/dismiss'})
                        }
        self.timeout = kwargs.pop('timeout', 15)

    def trigger_checkpoint(self):
        headers = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip',
            'Connection': 'keep-alive',
        }
        req = Request(self.endpoint, headers=headers)
        res = urlopen(req, timeout=15)

        csrf_mobj = re.search(r'csrftoken=(?P<csrf>[^;]+?);', res.info().get('set-cookie') or '')
        if not csrf_mobj:
            raise Exception('Unable to retrieve csrf token.')

        csrf = csrf_mobj.group('csrf')
        self.csrftoken = csrf

        cookie_val = res.info().get('set-cookie') or ''
        cookie = ''
        for c in ['sessionid', 'checkpoint_step', 'mid', 'csrftoken']:
            cookie_mobj = re.search(r'{0!s}=(?P<val>[^;]+?);'.format(c), cookie_val)
            if cookie_mobj:
                cookie += '{0!s}={1!s}; '.format(c, unquote_plus(cookie_mobj.group('val')))

        self.cookie = cookie
        data = {'csrfmiddlewaretoken': csrf, 'email': 'Verify by Email'}    # 'sms': 'Verify by SMS'

        headers['Referer'] = self.endpoint
        headers['Origin'] = 'https://i.instagram.com'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Cookie'] = self.cookie

        req = Request(self.endpoint, headers=headers)
        res = urlopen(req, data=urlencode(data).encode('ascii'), timeout=self.timeout)

        if res.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(res.read())
            content = gzip.GzipFile(fileobj=buf).read().decode('utf-8')
        else:
            content = res.read().decode('utf-8')

        if 'id_response_code' in content:
            return True

        return False

    def respond_to_checkpoint(self, response_code):
        headers = {
            'User-Agent': self.USER_AGENT,
            'Origin': 'https://i.instagram.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip',
            'Referer': self.endpoint,
            'Cookie': self.cookie,
        }

        req = Request(self.endpoint, headers=headers)
        data = {'csrfmiddlewaretoken': self.csrftoken, 'response_code': response_code}
        res = urlopen(req, data=urlencode(data).encode('ascii'), timeout=self.timeout)

        if res.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(res.read())
            content = gzip.GzipFile(fileobj=buf).read().decode('utf-8')
        else:
            content = res.read().decode('utf-8')

        return res.code, content


if __name__ == '__main__':
    print('------------------------------------')
    print('** THIS IS UNLIKELY TO BE WORKING **')
    print('------------------------------------')
    try:
        user_id = None
        while not user_id:
            user_id = input('User ID (numeric): ')

        client = Checkpoint(user_id)
        successful = client.trigger_checkpoint()

        if not successful:
            print('Unable to trigger checkpoint challenge.')

        response_code = None
        while not response_code:
            response_code = input('Response Code (6-digit numeric code): ')

        status_code, final_response = client.respond_to_checkpoint(response_code)

        if status_code != 200 or 'has been verified' not in final_response:
            print(final_response)
            print('-------------------------------\n[!] Unable to verify checkpoint.')
        else:
            print('[i] Checkpoint successfully verified.')

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print('Unexpected error: {0!s}'.format(str(e)))
