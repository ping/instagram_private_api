# Copyright (c) 2017 https://github.com/ping
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# -*- coding: utf-8 -*-

import logging
import hashlib
import json
import re
import gzip
from io import BytesIO
import time
import warnings
from functools import wraps
import string
import random
from socket import timeout, error as SocketError
from ssl import SSLError
from .compat import (
    compat_urllib_request, compat_urllib_parse,
    compat_urllib_parse_urlparse, compat_urllib_error,
    compat_http_client, compat_cookiejar
)
from .compatpatch import ClientCompatPatch
from .errors import (
    ClientError, ClientLoginError, ClientCookieExpiredError,
    ClientConnectionError
)
try:  # Python 3:
    # Not a no-op, we're adding this to the namespace so it can be imported.
    ConnectionError = ConnectionError       # pylint: disable=redefined-builtin
except NameError:  # Python 2:
    class ConnectionError(Exception):
        pass
from .http import ClientCookieJar, MultipartFormDataEncoder
from .common import ClientDeprecationWarning

logger = logging.getLogger(__name__)
warnings.simplefilter('always', ClientDeprecationWarning)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not args[0].is_authenticated:
            raise ClientError('Method requires authentication.', 403)
        return fn(*args, **kwargs)
    return wrapper


class Client(object):
    """Main API client class for the web api."""

    API_URL = 'https://www.instagram.com/query/'
    GRAPHQL_API_URL = 'https://www.instagram.com/graphql/query/'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5'    # noqa
    MOBILE_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 Mobile/15B93 Safari/604.1'     # noqa

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
        self.mobile_user_agent = (kwargs.pop('mobile_user_agent', None)
                                  or user_settings.get('mobile_user_agent')
                                  or self.MOBILE_USER_AGENT)

        self.init_csrftoken = None
        self.rhx_gis = kwargs.pop('rhx_gis', None) or user_settings.get('rhx_gis')

        cookie_string = kwargs.pop('cookie', None) or user_settings.get('cookie')
        cookie_jar = ClientCookieJar(cookie_string=cookie_string)
        if cookie_string and cookie_jar.auth_expires and int(time.time()) >= cookie_jar.auth_expires:
            raise ClientCookieExpiredError('Cookie expired at {0!s}'.format(cookie_jar.auth_expires))

        custom_ssl_context = kwargs.pop('custom_ssl_context', None)
        proxy_handler = None
        proxy = kwargs.pop('proxy', None)
        if proxy:
            warnings.warn('Proxy support is alpha.', UserWarning)
            parsed_url = compat_urllib_parse_urlparse(proxy)
            if parsed_url.netloc and parsed_url.scheme:
                proxy_address = '{0!s}://{1!s}'.format(parsed_url.scheme, parsed_url.netloc)
                proxy_handler = compat_urllib_request.ProxyHandler({'https': proxy_address})
            else:
                raise ValueError('Invalid proxy argument: {0!s}'.format(proxy))
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
        return self.get_cookie_value('csrftoken') or self.init_csrftoken

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
            'cookie': self.opener.cookie_jar.dump(),
            'created_ts': int(time.time()),
            'rhx_gis': self.rhx_gis,
            'user_agent': self.user_agent,
        }

    @staticmethod
    def _read_response(response):
        """
        Extract the response body from a http response.

        :param response:
        :return:
        """
        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(response.read())
            res = gzip.GzipFile(fileobj=buf).read().decode('utf8')
        else:
            res = response.read().decode('utf8')
        return res

    def generate_request_signature(self, query, endpoint=None):
        if self.rhx_gis and query.get('query_hash') and query.get('variables'):
            variables = query.get('variables')
        elif self.rhx_gis and '__a' in query and endpoint:
            variables = compat_urllib_parse_urlparse(endpoint).path
        else:
            return None

        m = hashlib.md5()
        m.update('{rhx_gis}:{variables}'.format(
            rhx_gis=self.rhx_gis,
            variables=variables
        ).encode('utf-8'))
        return m.hexdigest()

    def _make_request(self, url, params=None, headers=None, query=None,
                      return_response=False, get_method=None):
        """
        Calls the web API.

        :param url: fully formed api url
        :param params: post params
        :param headers: custom headers
        :param query: get url params
        :param return_response: bool flag to only return the http response object
        :param get_method: custom http method type
        :return:
        """
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
            sig = self.generate_request_signature(query, url)
            if sig:
                headers['X-Instagram-GIS'] = sig

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
            self.logger.debug('REQUEST: {0!s} {1!s}'.format(url, req.get_method()))
            self.logger.debug('REQ HEADERS: {0!s}'.format(
                ['{}: {}'.format(k, v) for k, v in headers.items()]
            ))
            self.logger.debug('REQ COOKIES: {0!s}'.format(
                ['{}: {}'.format(c.name, c.value) for c in self.cookie_jar]
            ))
            self.logger.debug('REQ DATA: {0!s}'.format(data))
            res = self.opener.open(req, data=data, timeout=self.timeout)

            self.logger.debug('RESPONSE: {0:d} {1!s}'.format(
                res.code, res.geturl()
            ))
            self.logger.debug('RES HEADERS: {0!s}'.format(
                [u'{}: {}'.format(k, v) for k, v in res.info().items()]
            ))
            if return_response:
                return res

            response_content = self._read_response(res)

            self.logger.debug('RES BODY: {0!s}'.format(response_content))
            return json.loads(response_content)

        except compat_urllib_error.HTTPError as e:
            raise ClientError('HTTPError "{0!s}" while opening {1!s}'.format(e.reason, url), e.code)
        except (SSLError, timeout, SocketError,
                compat_urllib_error.URLError,   # URLError is base of HTTPError
                compat_http_client.HTTPException,
                ConnectionError) as connection_error:
            raise ClientConnectionError('{} {}'.format(
                connection_error.__class__.__name__, str(connection_error)))

    @staticmethod
    def _sanitise_media_id(media_id):
        """The web API uses the numeric media ID only, and not the formatted one where it's XXXXX_YYY"""
        if re.match(r'[0-9]+_[0-9]+', media_id):    # endpoint uses the entirely numeric ID, not XXXX_YYY
            media_id = media_id.split('_')[0]
        return media_id

    @staticmethod
    def _extract_rhx_gis(html):
        mobj = re.search(
            r'"rhx_gis":"(?P<rhx_gis>[a-f0-9]{32})"', html, re.MULTILINE)
        if mobj:
            return mobj.group('rhx_gis')
        return None

    @staticmethod
    def _extract_csrftoken(html):
        mobj = re.search(
            r'"csrf_token":"(?P<csrf_token>[A-Za-z0-9]+)"', html, re.MULTILINE)

        if mobj:
            return mobj.group('csrf_token')
        return None

    def init(self):
        """Make a GET request to get the first csrf token and rhx_gis"""
        init_res = self._make_request(
            'https://www.instagram.com/', return_response=True, get_method=lambda: 'GET')
        init_res_content = self._read_response(init_res)

        rhx_gis = self._extract_rhx_gis(init_res_content)
        self.rhx_gis = rhx_gis

        if not self.csrftoken:
            csrftoken = self._extract_csrftoken(init_res_content)
            self.init_csrftoken = csrftoken

        if not self.csrftoken:
            raise ClientError('Unable to get csrf from init request.')
        if not self.rhx_gis:
            raise ClientError('Unable to get rhx_gis from init request.')
        # required to avoid 403 when doing unauthenticated requests
        self.cookie_jar.set_cookie(
            compat_cookiejar.Cookie(
                0, 'ig_pr', '1', None, False,
                'www.instagram.com', False, None, '/',
                False, False, None, True, None, None, {})
        )

    def login(self):
        """Login to the web site."""
        if not self.username or not self.password:
            raise ClientError('username/password is blank')
        params = {'username': self.username, 'password': self.password, 'queryParams': '{}'}
        login_res = self._make_request('https://www.instagram.com/accounts/login/ajax/', params=params)
        if not login_res.get('status', '') == 'ok' or not login_res.get('authenticated'):
            raise ClientLoginError('Unable to login')

        if self.on_login:
            on_login_callback = self.on_login
            on_login_callback(self)
        return login_res

    def user_info(self, user_id, **kwargs):     # pragma: no cover
        """
        OBSOLETE. Get user info.

        :param user_id: User id
        :param kwargs:
        :return:
        """
        warnings.warn(
            'This endpoint is obsolete. Do not use.', ClientDeprecationWarning)

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

    def user_info2(self, user_name, **kwargs):
        """
        Get user info.

        :param username: User name (not numeric ID)
        :param kwargs:
        :return:
        """
        # For authed and unauthed clients, a "fresh" rhx_gis must be used
        endpoint = 'https://www.instagram.com/{username!s}/'.format(**{'username': user_name})
        try:
            info = self._make_request(endpoint, query={'__a': '1'})
        except ClientError as ce:
            if ce.code != 403:
                raise ce
            # reinit to get a fresh rhx_gis
            self.init()
            info = self._make_request(endpoint, query={'__a': '1'})

        if self.auto_patch:
            ClientCompatPatch.user(info['graphql']['user'], drop_incompat_keys=self.drop_incompat_keys)
        return info['graphql']['user']

    def user_feed(self, user_id, **kwargs):
        """
        Get user feed

        :param user_id:
        :param kwargs:
            - **count**: Number of items to return. Default: 12
            - **end_cursor**: For pagination. Taken from:

                .. code-block:: python

                    info.get('data', {}).get('user', {}).get(
                        'edge_owner_to_timeline_media', {}).get(
                        'page_info', {}).get('end_cursor')
            - **extract**: bool. Return a simple list of media
        :return:
        """
        count = kwargs.pop('count', 12)
        if count > 50:
            raise ValueError('count cannot be greater than 50')

        end_cursor = kwargs.pop('end_cursor', None) or kwargs.pop('max_id', None)

        variables = {
            'id': user_id,
            'first': int(count),
        }
        if end_cursor:
            variables['after'] = end_cursor
        query = {
            'query_hash': '42323d64886122307be10013ad2dcc44',
            'variables': json.dumps(variables, separators=(',', ':'))
        }
        info = self._make_request(self.GRAPHQL_API_URL, query=query)

        if not info.get('data', {}).get('user'):
            # non-existent accounts do not return media at all
            # private accounts return media with just a count, no nodes
            raise ClientError('Not Found', 404)

        if self.auto_patch:
            [ClientCompatPatch.media(media['node'], drop_incompat_keys=self.drop_incompat_keys)
             for media in info.get('data', {}).get('user', {}).get(
                 'edge_owner_to_timeline_media', {}).get('edges', [])]

        if kwargs.pop('extract', True):
            return info.get('data', {}).get('user', {}).get(
                'edge_owner_to_timeline_media', {}).get('edges', [])
        return info

    def media_info(self, short_code, **kwargs):     # pragma: no cover
        """
        OBSOLETE. Get media info. Does not properly extract carousel media.

        :param short_code: A media's shortcode
        :param kwargs:
        :return:
        """
        warnings.warn(
            'This endpoint is obsolete. Do not use.', ClientDeprecationWarning)

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
            'https://www.instagram.com/p/{0!s}/'.format(short_code),
            query={'__a': '1', '__b': '1'},
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
            - **count**: Number of comments to return. Default: 16. Maximum: 50
            - **end_cursor**: For pagination
            - **extract**: bool. Return a simple list of comments
        :return:
        """
        count = kwargs.pop('count', 16)
        if count > 50:
            raise ValueError('count cannot be greater than 50')
        end_cursor = kwargs.pop('end_cursor', None)

        variables = {
            'shortcode': short_code,
            'first': int(count)
        }
        if end_cursor:
            variables['after'] = end_cursor
        query = {
            'query_hash': '33ba35852cb50da46f5b5e889df7d159',
            'variables': json.dumps(variables, separators=(',', ':'))
        }

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
    def media_likers(self, short_code, **kwargs):
        """
        Get media likers

        :param short_code:
        :param kwargs:
            - **count**: Number of likers to return. Default: 24. Maximum: 50
            - **end_cursor**: For pagination
            - **extract**: bool. Return a simple list of likers
        :return:
        """
        end_cursor = kwargs.pop('end_cursor', None)
        # request 24 by default for the first page
        if end_cursor:
            count = kwargs.pop('count', 12)
        else:
            count = kwargs.pop('count', 24)
        if count > 50:
            raise ValueError('count cannot be greater than 50')

        variables = {
            'shortcode': short_code,
            'first': int(count)
        }
        if end_cursor:
            variables['after'] = end_cursor
        query = {
            'query_hash': '1cb6ec562846122743b61e492c85999f',
            'variables': json.dumps(variables, separators=(',', ':'))
        }

        info = self._make_request(self.GRAPHQL_API_URL, query=query)

        if not info.get('data', {}).get('shortcode_media'):
            # deleted media does not return 'likers' at all
            # media without likes will return likes, with counts = 0, nodes = [], etc
            raise ClientError('Not Found', 404)

        if kwargs.pop('extract', True):
            return [c['node'] for c in info.get('data', {}).get('shortcode_media', {}).get(
                'edge_liked_by', {}).get('edges', [])]
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
        if count > 50:
            raise ValueError('count cannot be greater than 50')

        end_cursor = kwargs.pop('end_cursor', None)
        variables = {
            'id': user_id,
            'first': int(count)
        }
        if end_cursor:
            variables['after'] = end_cursor

        query = {
            'query_hash': '58712303d941c6855d4e888c5f0cd22f',
            'variables': json.dumps(variables, separators=(',', ':'))
        }

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
        if count > 50:
            raise ValueError('count cannot be greater than 50')

        end_cursor = kwargs.pop('end_cursor', None)
        variables = {
            'id': user_id,
            'first': int(count)
        }
        if end_cursor:
            variables['after'] = end_cursor

        query = {
            'query_hash': '37479f2b8209594dde7facb0d904896a',
            'variables': json.dumps(variables, separators=(',', ':'))
        }

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
        endpoint = 'https://www.instagram.com/web/likes/{media_id!s}/like/'.format(**{'media_id': media_id})
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
        endpoint = 'https://www.instagram.com/web/likes/{media_id!s}/unlike/'.format(**{'media_id': media_id})
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
        endpoint = 'https://www.instagram.com/web/friendships/{user_id!s}/follow/'.format(**{'user_id': user_id})
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
        endpoint = 'https://www.instagram.com/web/friendships/{user_id!s}/unfollow/'.format(**{'user_id': user_id})
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
                    "id": "1785800000"
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
        endpoint = 'https://www.instagram.com/web/comments/{media_id!s}/add/'.format(**{'media_id': media_id})
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
        endpoint = 'https://www.instagram.com/web/comments/{media_id!s}/delete/{comment_id!s}/'.format(**{
            'media_id': media_id, 'comment_id': comment_id})
        return self._make_request(endpoint, params='')

    def search(self, query_text):
        """
        General search

        :param query_text: Search text
        :return:
        """
        endpoint = 'https://www.instagram.com/web/search/topsearch/'
        res = self._make_request(endpoint, query={'query': query_text})
        if self.auto_patch:
            for u in res.get('users', []):
                ClientCompatPatch.list_user(u['user'])
        return res

    @login_required
    def post_photo(self, photo_data, caption=''):
        """
        Post a photo

        :param photo_data: byte string of the image
        :param caption: caption text
        """
        warnings.warn('This endpoint has not been fully tested.', UserWarning)

        upload_id = int(time.time() * 1000)
        boundary = '----WebKitFormBoundary{}'.format(
            ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)))
        fields = [
            ('upload_id', upload_id),
            ('media_type', 1),
        ]
        files = [
            ('photo', 'photo.jpg', 'application/octet-stream', photo_data)
        ]
        content_type, body = MultipartFormDataEncoder(boundary=boundary).encode(
            fields, files)
        headers = {
            'User-Agent': self.mobile_user_agent,
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'x-csrftoken': self.csrftoken,
            'x-requested-with': 'XMLHttpRequest',
            'x-instagram-ajax': '1',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/create/crop/',
            'Content-Type': content_type,
            'Content-Length': len(body)
        }
        endpoint = 'https://www.instagram.com/create/upload/photo/'
        req = compat_urllib_request.Request(endpoint, body, headers=headers)
        self.logger.debug('REQUEST: {0!s}'.format(endpoint))

        try:
            res = self.opener.open(req, timeout=self.timeout)
            response_content = self._read_response(res)

            self.logger.debug('RESPONSE: {0!s}'.format(response_content))
            upload_res = json.loads(response_content)
            if upload_res.get('status', '') != 'ok':
                raise ClientError('Upload status: {}'.format(upload_res.get('status', '')))
            upload_id = upload_res['upload_id']

            headers['Referer'] = 'https://www.instagram.com/create/details/'
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            del headers['Content-Length']
            endpoint = 'https://www.instagram.com/create/configure/'
            res = self._make_request(
                endpoint, headers=headers,
                params={'upload_id': upload_id, 'caption': caption},
                get_method=lambda: 'POST')
            return res

        except compat_urllib_error.HTTPError as e:
            raise ClientError('HTTPError "{0!s}" while opening {1!s}'.format(e.reason, endpoint), e.code)

    def tag_feed(self, tag, **kwargs):
        """
        Get a tag feed.

        :param tag:
        :param kwargs:
            - **count**: Number of records to return
            - **end_cursor**: For pagination
        :return:
        """
        count = kwargs.pop('count', 16)
        if count > 50:
            raise ValueError('count cannot be greater than 50')

        end_cursor = kwargs.pop('end_cursor', None) or kwargs.pop('max_id', None)

        variables = {
            'tag_name': tag,
            'first': int(count)
        }
        if end_cursor:
            variables['after'] = end_cursor
        query = {
            'query_hash': 'ded47faa9a1aaded10161a2ff32abb6b',
            'variables': json.dumps(variables, separators=(',', ':'))
        }

        return self._make_request(self.GRAPHQL_API_URL, query=query)

    def location_feed(self, location_id, **kwargs):
        """
        Get a location feed.

        :param location_id:
        :param kwargs:
            - **count**: Number of records to return
            - **end_cursor**: For pagination
        :return:
        """
        count = kwargs.pop('count', 16)
        if count > 50:
            raise ValueError('count cannot be greater than 50')

        end_cursor = kwargs.pop('end_cursor', None) or kwargs.pop('max_id', None)

        variables = {
            'id': location_id,
            'first': int(count)
        }
        if end_cursor:
            variables['after'] = end_cursor

        query = {
            'query_hash': 'ac38b90f0f3981c42092016a37c59bf7',
            'variables': json.dumps(variables, separators=(',', ':'))
        }

        return self._make_request(self.GRAPHQL_API_URL, query=query)

    @login_required
    def timeline_feed(self, **kwargs):
        """
        Get logged-in user's timeline feed.

        :param kwargs:
            - **count**: Number of records to return
            - **end_cursor**: For pagination
        """
        end_cursor = kwargs.pop('end_cursor', None) or kwargs.pop('max_id', None)
        fetch_media_item_count = int(kwargs.pop('count', 12))
        if fetch_media_item_count > 50:
            raise ValueError('count cannot be greater than 50')

        fetch_comment_count = int(kwargs.pop('fetch_comment_count', 4))
        fetch_like = int(kwargs.pop('fetch_like', 10))
        has_stories = bool(kwargs.pop('has_stories', False))
        variables = {
            'fetch_media_item_count': fetch_media_item_count,
            'fetch_comment_count': fetch_comment_count,
            'fetch_like': fetch_like,
            'has_stories': has_stories,
        }
        if end_cursor:
            variables['fetch_media_item_cursor'] = end_cursor
        query = {
            'query_hash': '485c25657308f08317c1e4b967356828',
            'variables': json.dumps(variables, separators=(',', ':'))
        }
        return self._make_request(self.GRAPHQL_API_URL, query=query)

    @login_required
    def reels_tray(self):
        """
        Get a logged-in users reels tray.
        """
        query = {
            'query_hash': '60b755363b5c230111347a7a4e242001',
            'variables': json.dumps({'only_stories': False}, separators=(',', ':'))
        }
        return self._make_request(self.GRAPHQL_API_URL, query=query)

    @login_required
    def reels_feed(self, reel_ids, **kwargs):
        """
        Get the stories feed for the specified user IDs

        :param reel_ids: List of reel user IDs
        """
        variables = {
            'reel_ids': reel_ids,
            'tag_names': kwargs.pop('tag_names', []),
            'location_ids': kwargs.pop('location_ids', []),
            'precomposed_overlay': False,
        }
        query = {
            'query_hash': '45246d3fe16ccc6577e0bd297a5db1ab',
            'variables': json.dumps(variables, separators=(',', ':'))
        }
        return self._make_request(self.GRAPHQL_API_URL, query=query)
