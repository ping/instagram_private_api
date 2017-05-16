# -*- coding: utf-8 -*-

import logging
import json
import re
import gzip
from io import BytesIO
import time
import warnings
from functools import wraps

from .compat import (
    compat_pickle, compat_cookiejar, compat_urllib_request,
    compat_urllib_parse, compat_urllib_parse_urlparse, compat_urllib_error
)
from .compatpatch import ClientCompatPatch
from .errors import ClientError, ClientLoginError, ClientCookieExpiredError

logger = logging.getLogger(__name__)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not args[0].is_authenticated:
            raise ClientError('Method requires authentication.', 403)
        return fn(*args, **kwargs)
    return wrapper


class Client(object):

    API_URL = 'https://www.instagram.com/query/'
    GRAPHQL_API_URL = 'https://www.instagram.com/graphql/query/'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) ' \
                 'Version/9.1.1 Safari/601.6.17'

    def __init__(self, user_agent=None, **kwargs):
        """

        :param user_agent: Override the default useragent string with your own
        :param kwargs: See below

        :Keyword Arguments:
            - **auto_patch**: Patch the api objects to match the public API. Default: False
            - **drop_incompat_key**: Remove api object keys that is not in the public API. Default: False
            - **timeout**: Timeout interval in seconds. Default: 10
            - **username**: Login username
            - **password**: Login password
            - **authenticate**: Do login on init
            - **cookie**: Saved cookie string from a previous session
            - **settings**: A dict of settings from a previous session
            - **on_login**: Callback after successful login
            - **proxy**: Specify a proxy ex: 'http://127.0.0.1:8888' (ALPHA)
        :return:
        """
        self.auto_patch = kwargs.pop('auto_patch', False)
        self.drop_incompat_keys = kwargs.pop('drop_incompat_keys', False)
        self.timeout = kwargs.pop('timeout', 10)
        self.username = kwargs.pop('username', None)
        self.password = kwargs.pop('password', None)
        self.authenticate = kwargs.pop('authenticate', False)
        self.on_login = kwargs.pop('on_login', None)
        user_settings = kwargs.pop('settings', None) or {}
        self.user_agent = user_agent or user_settings.get('user_agent') or self.USER_AGENT

        cookie_string = kwargs.pop('cookie', None) or user_settings.get('cookie')
        cookie_jar = ClientCookieJar(cookie_string=cookie_string)
        if cookie_string and cookie_jar.expires_earliest and int(time.time()) >= cookie_jar.expires_earliest:
            raise ClientCookieExpiredError('Oldest cookie expired at %s' % cookie_jar.expires_earliest)

        custom_ssl_context = kwargs.pop('custom_ssl_context', None)
        proxy_handler = None
        proxy = kwargs.pop('proxy', None)
        if proxy:
            warnings.warn('Proxy support is alpha.', UserWarning)
            parsed_url = compat_urllib_parse_urlparse(proxy)
            if parsed_url.netloc and parsed_url.scheme:
                proxy_address = '%s://%s' % (parsed_url.scheme, parsed_url.netloc)
                proxy_handler = compat_urllib_request.ProxyHandler({'https': proxy_address})
            else:
                raise ValueError('Invalid proxy argument: %s' % proxy)
        handlers = []
        if proxy_handler:
            handlers.append(proxy_handler)
        cookie_handler = compat_urllib_request.HTTPCookieProcessor(cookie_jar)
        try:
            httpshandler = compat_urllib_request.HTTPSHandler(context=custom_ssl_context)
        except TypeError:
            # py version < 2.7.9
            httpshandler = compat_urllib_request.HTTPSHandler()

        handlers.extend([
            compat_urllib_request.HTTPHandler(),
            httpshandler,
            cookie_handler])
        opener = compat_urllib_request.build_opener(*handlers)
        opener.cookie_jar = cookie_jar
        self.opener = opener

        self.logger = logger
        if not self.csrftoken:
            self.init()
        if not self.is_authenticated and self.authenticate and self.username and self.password:
            self.login()

    @property
    def cookie_jar(self):
        return self.opener.cookie_jar

    def get_cookie_value(self, key):
        for cookie in self.cookie_jar:
            if cookie.name.lower() == key.lower():
                return cookie.value
        return None

    @property
    def csrftoken(self):
        """The client's current csrf token"""
        return self.get_cookie_value('csrftoken')

    @property
    def authenticated_user_id(self):
        """The current authenticated user id"""
        return self.get_cookie_value('ds_user_id')

    @property
    def authenticated_user_name(self):
        """The current authenticated user name. No longer available."""
        warnings.warn('No longer available.', DeprecationWarning)
        return self.get_cookie_value('ds_user')

    @property
    def is_authenticated(self):
        if self.authenticated_user_id:
            return True
        return False

    @property
    def settings(self):
        """Helper property that extracts the settings that you should cache
        in addition to username and password."""
        return {
            'user_agent': self.user_agent,
            'cookie': self.opener.cookie_jar.dump(),
            'created_ts': int(time.time())
        }

    def _make_request(self, url, params=None, headers=None, query=None, return_response=False, get_method=None):
        if not headers:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Accept-Language': 'en-US',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'close',
            }
            if params or params == '':
                headers.update({
                    'x-csrftoken': self.csrftoken,
                    'x-requested-with': 'XMLHttpRequest',
                    'x-instagram-ajax': '1',
                    'Referer': 'https://www.instagram.com',
                    'Authority': 'www.instagram.com',
                    'Origin': 'https://www.instagram.com',
                    'Content-Type': 'application/x-www-form-urlencoded'
                })
        if query:
            url += ('?' if '?' not in url else '&') + compat_urllib_parse.urlencode(query)
        req = compat_urllib_request.Request(url, headers=headers)
        if get_method:
            req.get_method = get_method

        data = None
        if params or params == '':
            if params == '':    # force post if empty string
                data = ''.encode('ascii')
            else:
                data = compat_urllib_parse.urlencode(params).encode('ascii')
        try:
            self.logger.debug('REQUEST: %s %s' % (url, req.get_method()))
            self.logger.debug('DATA: %s' % data)
            res = self.opener.open(req, data=data, timeout=self.timeout)
            if return_response:
                return res

            if res.info().get('Content-Encoding') == 'gzip':
                buf = BytesIO(res.read())
                response_content = gzip.GzipFile(fileobj=buf).read().decode('utf8')
            else:
                response_content = res.read().decode('utf8')

            self.logger.debug('RESPONSE: %s' % response_content)
            return json.loads(response_content)

        except compat_urllib_error.HTTPError as e:
            raise ClientError('HTTPError "%s" while opening %s' % (e.reason, url), e.code)
        except compat_urllib_error.URLError as e:
            raise ClientError('URLError "%s" while opening %s' % (e.reason, url))

    def _sanitise_media_id(self, media_id):
        """The web API uses the numeric media ID only, and not the formatted one where it's XXXXX_YYY"""
        if re.match(r'[0-9]+_[0-9]+', media_id):    # endpoint uses the entirely numeric ID, not XXXX_YYY
            media_id = media_id.split('_')[0]
        return media_id

    def init(self):
        """Make a HEAD request to get the first csrf token"""
        self._make_request(
            'https://www.instagram.com/', return_response=True, get_method=lambda: 'HEAD')
        if not self.csrftoken:
            raise ClientError('Unable to get csrf from init request.')

    def login(self):
        if not self.username or not self.password:
            raise ClientError('username/password is blank')
        params = {'username': self.username, 'password': self.password}
        login_res = self._make_request('https://www.instagram.com/accounts/login/ajax/', params=params)
        if not login_res.get('status', '') == 'ok' or not login_res.get('authenticated'):
            raise ClientLoginError('Unable to login')

        if self.on_login:
            on_login_callback = self.on_login
            on_login_callback(self)
        return login_res

    def user_info(self, user_id, **kwargs):
        """
        Get user info

        :param user_id: User id
        :param kwargs:
        :return:
        """
        params = {
            'q': 'ig_user(%(user_id)s) {id, username, full_name, profile_pic_url, '
                 'biography, external_url, is_private, is_verified, '
                 'media {count}, followed_by {count}, follows {count} }' % {'user_id': user_id},
        }
        user = self._make_request(self.API_URL, params=params)

        if not user.get('id'):
            raise ClientError('Not Found', 404)

        if self.auto_patch:
            user = ClientCompatPatch.user(user, drop_incompat_keys=self.drop_incompat_keys)
        return user

    def user_feed(self, user_id, **kwargs):
        """
        Get user feed

        :param user_id:
        :param kwargs:
            - **count**: Number of items to return. Default: 16
            - **min_media_id** / **end_cursor**: For pagination
            - **extract**: bool. Return a simple list of media
        :return:
        """

        count = kwargs.pop('count', 16)
        min_media_id = kwargs.pop('min_media_id', None) or kwargs.pop('end_cursor', None)
        if not min_media_id:
            command = 'media.first(%(count)d)' % {'count': count}
        else:
            command = 'media.after(%(min_id)s, %(count)d)' % {'count': count, 'min_id': min_media_id}
        params = {
            'q': 'ig_user(%(user_id)s) {%(command)s {count, nodes {'
                 'caption, code, comments {count}, date, dimensions {height, width}, comments_disabled, '
                 'usertags {nodes {x, y, user {id, username, full_name, profile_pic_url} }}, '
                 'location {id, name, lat, lng}, display_src, id, is_video, is_ad, '
                 'likes {count}, owner {id, username, full_name, profile_pic_url, '
                 'is_verified, is_private }, '
                 '__typename, thumbnail_src, video_views, video_url}, page_info}}' % {
                     'user_id': user_id, 'count': count, 'command': command},
            'ref': 'tags::show'
        }
        info = self._make_request(self.API_URL, params=params)
        if not info.get('media'):
            # non-existent accounts do not return media at all
            # private accounts return media with just a count, no nodes
            raise ClientError('Not Found', 404)

        if self.auto_patch:
            [ClientCompatPatch.media(media, drop_incompat_keys=self.drop_incompat_keys)
             for media in info.get('media', {}).get('nodes', [])]

        if kwargs.pop('extract', True):
            return info.get('media', {}).get('nodes', [])
        return info

    def media_info(self, short_code, **kwargs):
        """
        Get media info. Does not properly extract carousel media.

        :param short_code: A media's shortcode
        :param kwargs:
        :return:
        """
        params = {
            'q': 'ig_shortcode(%(media_code)s) { caption, code, comments {count}, date, '
                 'dimensions {height, width}, comments_disabled, '
                 'usertags {nodes {x, y, user {id, username, full_name, profile_pic_url} }}, '
                 'location {id, name, lat, lng}, display_src, id, is_video, is_ad, '
                 'likes {count}, owner {id, username, full_name, profile_pic_url, '
                 'is_private, is_verified}, __typename, '
                 'thumbnail_src, video_views, video_url }' % {'media_code': short_code}
        }
        media = self._make_request(self.API_URL, params=params)
        if not media.get('code'):
            raise ClientError('Not Found', 404)

        if self.auto_patch:
            media = ClientCompatPatch.media(media, drop_incompat_keys=self.drop_incompat_keys)
        return media

    def media_info2(self, short_code):
        """
        Alternative method to get media info. This method works for carousel media.

        :param short_code: A media's shortcode
        :param kwargs:
        :return:
        """
        headers = {
            'User-Agent': self.user_agent,
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Referer': 'https://www.instagram.com',
            'x-requested-with': 'XMLHttpRequest',
        }
        info = self._make_request(
            'https://www.instagram.com/p/%s/?__a=1&__b=1' % short_code,
            headers=headers)
        media = info.get('graphql', {}).get('shortcode_media', {})
        if self.auto_patch:
            media = ClientCompatPatch.media(media, drop_incompat_keys=self.drop_incompat_keys)
        return media

    def media_comments(self, short_code, **kwargs):
        """
        Get media comments

        :param short_code:
        :param kwargs:
            - **count**: Number of comments to return. Default: 16. Maximum: 1000
            - **before_comment_id**: For pagination
            - **extract**: bool. Return a simple list of comments
        :return:
        """
        count = kwargs.pop('count', 16)
        end_cursor = kwargs.pop('end_cursor', None)

        query = {
            'query_id': '17852405266163336',
            'shortcode': short_code,
            'first': count}

        if end_cursor:
            query['after'] = end_cursor
        info = self._make_request(self.GRAPHQL_API_URL, query=query)

        if not info.get('data', {}).get('shortcode_media'):
            # deleted media does not return 'comments' at all
            # media without comments will return comments, with counts = 0, nodes = [], etc
            raise ClientError('Not Found', 404)

        if self.auto_patch:
            [ClientCompatPatch.comment(c['node'], drop_incompat_keys=self.drop_incompat_keys)
             for c in info.get('data', {}).get('shortcode_media', {}).get(
                 'edge_media_to_comment', {}).get('edges', [])]

        if kwargs.pop('extract', True):
            return [c['node'] for c in info.get('data', {}).get('shortcode_media', {}).get(
                'edge_media_to_comment', {}).get('edges', [])]
        return info

    @login_required
    def user_following(self, user_id, **kwargs):
        """
        Get user's followings. Login required.

        :param user_id: User id of account
        :param kwargs:
            - **count**: Number of followings. Default: 10
            - **end_cursor**: For pagination
            - **extract**: bool. Return a simple list of users
        :return:
        """
        count = kwargs.pop('count', 10)
        end_cursor = kwargs.pop('end_cursor', None)
        query = {
            'query_id': '17874545323001329',
            'id': user_id,
            'first': count,
        }
        if end_cursor:
            query['after'] = end_cursor

        info = self._make_request(self.GRAPHQL_API_URL, query=query)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u['node'], drop_incompat_keys=self.drop_incompat_keys)
             for u in info.get('data', {}).get('user', {}).get(
                 'edge_follow', {}).get('edges', [])]

        if kwargs.pop('extract', True):
            return [u['node'] for u in info.get('data', {}).get('user', {}).get(
                'edge_follow', {}).get('edges', [])]
        return info

    @login_required
    def user_followers(self, user_id, **kwargs):
        """
        Get a user's followers. Login required.

        :param user_id: User id of account
        :param kwargs:
            - **count**: Number of followers. Default: 10
            - **end_cursor**: For pagination
            - **extract**: bool. Return a simple list of users
        :return:
        """
        count = kwargs.pop('count', 10)
        end_cursor = kwargs.pop('end_cursor', None)
        query = {
            'query_id': '17851374694183129',
            'id': user_id,
            'first': count,
        }
        if end_cursor:
            query['after'] = end_cursor

        info = self._make_request(self.GRAPHQL_API_URL, query=query)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u['node'], drop_incompat_keys=self.drop_incompat_keys)
             for u in info.get('data', {}).get('user', {}).get(
                 'edge_followed_by', {}).get('edges', [])]

        if kwargs.pop('extract', True):
            return [u['node'] for u in info.get('data', {}).get('user', {}).get(
                'edge_followed_by', {}).get('edges', [])]
        return info

    @login_required
    def post_like(self, media_id):
        """
        Like an update. Login required.

        :param media_id: Media id
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        media_id = self._sanitise_media_id(media_id)
        endpoint = 'https://www.instagram.com/web/likes/%(media_id)s/like/' % {'media_id': media_id}
        res = self._make_request(endpoint, params='')
        return res

    @login_required
    def delete_like(self, media_id):
        """
        Unlike an update. Login required.

        :param media_id: Media id
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        media_id = self._sanitise_media_id(media_id)
        endpoint = 'https://www.instagram.com/web/likes/%(media_id)s/unlike/' % {'media_id': media_id}
        return self._make_request(endpoint, params='')

    @login_required
    def friendships_create(self, user_id):
        """
        Follow a user. Login required.

        :param user_id: User id
        :return:
            .. code-block:: javascript

                {"status": "ok", "result": "following"}
        """
        endpoint = 'https://www.instagram.com/web/friendships/%(user_id)s/follow/' % {'user_id': user_id}
        return self._make_request(endpoint, params='')

    @login_required
    def friendships_destroy(self, user_id):
        """
        Unfollow a user. Login required.

        :param user_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'https://www.instagram.com/web/friendships/%(user_id)s/unfollow/' % {'user_id': user_id}
        return self._make_request(endpoint, params='')

    @login_required
    def post_comment(self, media_id, comment_text):
        """
        Post a new comment. Login required.

        :param media_id: Media id (all numeric format, without _userid)
        :param comment_text: Comment text
        :return:
            .. code-block:: javascript

                {
                    "created_time": 1483096000,
                    "text": "This is a comment",
                    "status": "ok",
                    "from": {
                        "username": "somebody",
                        "profile_picture": "https://igcdn-photos-b-a.akamaihd.net/something.jpg",
                        "id": "1234567890",
                        "full_name": "Somebody"
                    },
                    "id": "1785811280000000"
                }
        """
        if len(comment_text) > 300:
            raise ValueError('The total length of the comment cannot exceed 300 characters.')
        if re.search(r'[a-z]+', comment_text, re.IGNORECASE) and comment_text == comment_text.upper():
            raise ValueError('The comment cannot consist of all capital letters.')
        if len(re.findall(r'#[^#]+\b', comment_text, re.UNICODE | re.MULTILINE)) > 4:
            raise ValueError('The comment cannot contain more than 4 hashtags.')
        if len(re.findall(r'\bhttps?://\S+\.\S+', comment_text)) > 1:
            raise ValueError('The comment cannot contain more than 1 URL.')

        media_id = self._sanitise_media_id(media_id)
        endpoint = 'https://www.instagram.com/web/comments/%(media_id)s/add/' % {'media_id': media_id}
        params = {'comment_text': comment_text}
        return self._make_request(endpoint, params=params)

    @login_required
    def delete_comment(self, media_id, comment_id):
        """
        Delete a comment. Login required.

        :param media_id: Media id
        :param comment_id: Comment id
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        media_id = self._sanitise_media_id(media_id)
        endpoint = 'https://www.instagram.com/web/comments/%(media_id)s/delete/%(comment_id)s/' % {
            'media_id': media_id, 'comment_id': comment_id}
        return self._make_request(endpoint, params='')

    def search(self, query_text):
        """
        General search

        :param query_text: Search text
        :return:
        """
        endpoint = 'https://www.instagram.com/web/search/topsearch/?' + compat_urllib_parse.urlencode(
            {'query': query_text})
        res = self._make_request(endpoint)
        if self.auto_patch:
            for u in res.get('users', []):
                ClientCompatPatch.list_user(u['user'])
        return res


class ClientCookieJar(compat_cookiejar.CookieJar):
    """Custom CookieJar that can be pickled to/from strings
    """
    def __init__(self, cookie_string=None, policy=None):
        compat_cookiejar.CookieJar.__init__(self, policy)
        if cookie_string:
            if isinstance(cookie_string, bytes):
                self._cookies = compat_pickle.loads(cookie_string)
            else:
                self._cookies = compat_pickle.loads(cookie_string.encode('utf-8'))

    @property
    def expires_earliest(self):
        if len(self) > 0:
            return min([cookie.expires for cookie in self if cookie.expires])
        return None

    def dump(self):
        return compat_pickle.dumps(self._cookies)
