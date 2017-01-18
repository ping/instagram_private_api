# -*- coding: utf-8 -*-

import logging
import hmac
import hashlib
import uuid
import json
import re
import time
import gzip
from io import BytesIO
import warnings
try:
    # python 2.x
    from urllib2 import urlopen, build_opener, HTTPCookieProcessor, HTTPHandler, HTTPSHandler, ProxyHandler, Request, HTTPError
    from urllib import urlencode
    from urlparse import urlparse
except ImportError:
    # python 3.x
    from urllib.request import urlopen, build_opener, HTTPCookieProcessor, HTTPHandler, HTTPSHandler, ProxyHandler, Request
    from urllib.error import HTTPError
    from urllib.parse import urlencode, urlparse

from .compatpatch import ClientCompatPatch
from .errors import ClientError, ClientLoginError, ClientLoginRequiredError, ClientCookieExpiredError
from .constants import Constants
from .http import ClientCookieJar, MultipartFormDataEncoder
from .utils import max_chunk_count_generator, gen_user_breadcrumb

logger = logging.getLogger(__name__)


class Client(object):

    API_URL = 'https://i.instagram.com/api/v1/'

    USER_AGENT = Constants.USER_AGENT
    IG_SIG_KEY = Constants.IG_SIG_KEY
    IG_CAPABILITIES = Constants.IG_CAPABILITIES
    SIG_KEY_VERSION = Constants.SIG_KEY_VERSION
    EXTERNAL_LOC_SOURCES = {
        'foursquare': 'foursquare_v2_id',
        'facebook_places': 'facebook_places_id',
        'facebook_events': 'facebook_events_id'
    }

    def __init__(self, username, password, **kwargs):
        """

        :param username: Login usernam
        :param password: Login password
        :param kwargs: See below

        :Keyword Arguments:
            - **auto_patch**: Patch the api objects to match the public API. Default: False
            - **drop_incompat_key**: Remove api object keys that is not in the public API. Default: False
            - **timeout**: Timeout interval in seconds. Default: 15
            - **api_url**: Override the default api url base
            - **cookie**: Saved cookie string from a previous session
            - **settings**: A dict of settings from a previous session
            - **on_login**: Callback after successful login
            - **proxy**: Specify a proxy ex: 'http://127.0.0.1:8888' (ALPHA)
        :return:
        """
        """
        Key arguments:
        auto_patch -- whether to automatically patch entities for compatibility
        drop_incompat_keys -- whether to remove incompatible entity keys
        """
        self.username = username
        self.password = password
        self.auto_patch = kwargs.pop('auto_patch', False)
        self.drop_incompat_keys = kwargs.pop('drop_incompat_keys', False)
        self.api_url = kwargs.pop('api_url', None) or self.API_URL
        self.timeout = kwargs.pop('timeout', 15)
        self.on_login = kwargs.pop('on_login', None)
        self.logger = logger

        user_settings = kwargs.pop('settings', None) or {}
        self.uuid = (
            kwargs.pop('guid', None) or kwargs.pop('uuid', None) or
            user_settings.get('uuid') or self.generate_uuid(False))
        self.device_id = (
            kwargs.pop('device_id', None) or user_settings.get('device_id') or
            self.generate_deviceid())
        self.signature_key = (
            kwargs.pop('signature_key', None) or user_settings.get('signature_key') or
            self.IG_SIG_KEY)
        self.key_version = (
            kwargs.pop('key_version', None) or user_settings.get('key_version') or
            self.SIG_KEY_VERSION)
        self.ig_capabilities = (
            kwargs.pop('ig_capabilities', None) or user_settings.get('ig_capabilities')or
            self.IG_CAPABILITIES)

        # to maintain backward compat for user_agent kwarg
        custom_ua = kwargs.pop('user_agent', '') or user_settings.get('user_agent')
        if custom_ua:
            self.user_agent = custom_ua
        else:
            self.app_version = (
                kwargs.pop('app_version', None) or user_settings.get('app_version') or
                Constants.APP_VERSION)
            self.android_release = (
                kwargs.pop('android_release', None) or user_settings.get('android_release') or
                Constants.ANDROID_RELEASE)
            self.android_version = int(
                kwargs.pop('android_version', None) or user_settings.get('android_version') or
                Constants.ANDROID_VERSION)
            self.phone_manufacturer = (
                kwargs.pop('phone_manufacturer', None) or user_settings.get('phone_manufacturer') or
                Constants.PHONE_MANUFACTURER)
            self.phone_device = (
                kwargs.pop('phone_device', None) or user_settings.get('phone_device') or
                Constants.PHONE_DEVICE)
            self.phone_model = (
                kwargs.pop('phone_model', None) or user_settings.get('phone_model') or
                Constants.PHONE_MODEL)
            self.phone_dpi = (
                kwargs.pop('phone_dpi', None) or user_settings.get('phone_dpi') or
                Constants.PHONE_DPI)
            self.phone_resolution = (
                kwargs.pop('phone_resolution', None) or user_settings.get('phone_resolution') or
                Constants.PHONE_RESOLUTION)
            self.phone_chipset = (
                kwargs.pop('phone_chipset', None) or user_settings.get('phone_chipset') or
                Constants.PHONE_CHIPSET)

        cookie_string = kwargs.pop('cookie', None) or user_settings.get('cookie')
        cookie_jar = ClientCookieJar(cookie_string=cookie_string)
        if cookie_string and cookie_jar.expires_earliest and int(time.time()) >= cookie_jar.expires_earliest:
            raise ClientCookieExpiredError('Oldest cookie expired at %s' % cookie_jar.expires_earliest)
        cookie_handler = HTTPCookieProcessor(cookie_jar)

        custom_ssl_context = kwargs.pop('custom_ssl_context', None)
        proxy_handler = None
        proxy = kwargs.pop('proxy', None)
        if proxy:
            warnings.warn('Proxy support is alpha.', UserWarning)
            parsed_url = urlparse(proxy)
            if parsed_url.netloc and parsed_url.scheme:
                proxy_address = '%s://%s' % (parsed_url.scheme, parsed_url.netloc)
                proxy_handler = ProxyHandler({'https': proxy_address})
            else:
                raise ClientError('Invalid proxy argument: %s' % proxy)
        handlers = []
        if proxy_handler:
            handlers.append(proxy_handler)
        try:
            httpshandler = HTTPSHandler(context=custom_ssl_context)
        except TypeError as e:
            # py version < 2.7.9
            httpshandler = HTTPSHandler()

        handlers.extend([
            HTTPHandler(),
            httpshandler,
            cookie_handler])
        opener = build_opener(*handlers)
        opener.cookie_jar = cookie_jar
        self.opener = opener

        if not cookie_string:   # or not self.token or not self.rank_token:
            self.login()

    @property
    def settings(self):
        """Helper property that extracts the settings that you should cache
        in addition to username and password."""
        return {
            'uuid': self.uuid,
            'device_id': self.device_id,
            'signature_key': self.signature_key,
            'key_version': self.key_version,
            'ig_capabilities': self.ig_capabilities,
            'app_version': self.app_version,
            'android_release': self.android_release,
            'android_version': self.android_version,
            'phone_manufacturer': self.phone_manufacturer,
            'phone_device': self.phone_device,
            'phone_model': self.phone_model,
            'phone_dpi': self.phone_dpi,
            'phone_resolution': self.phone_resolution,
            'phone_chipset': self.phone_chipset,
            'cookie': self.opener.cookie_jar.dump(),
            'created_ts': int(time.time())
        }

    @property
    def user_agent(self):
        """Returns the useragent string that the client is currently using."""
        return Constants.USER_AGENT_FORMAT % {
            'app_version': self.app_version,
            'android_version': self.android_version,
            'android_release': self.android_release,
            'brand': self.phone_manufacturer,
            'device': self.phone_device,
            'model': self.phone_model,
            'dpi': self.phone_dpi,
            'resolution': self.phone_resolution,
            'chipset': self.phone_chipset}

    @user_agent.setter
    def user_agent(self, value):
        """Override the useragent string with your own"""
        mobj = re.search(Constants.USER_AGENT_EXPRESSION, value)
        if not mobj:
            raise ValueError('User-agent specified does not fit format required: %s' %
                             Constants.USER_AGENT_EXPRESSION)
        self.app_version = mobj.group('app_version')
        self.android_release = mobj.group('android_release')
        self.android_version = int(mobj.group('android_version'))
        self.phone_manufacturer = mobj.group('manufacturer')
        self.phone_device = mobj.group('device')
        self.phone_model = mobj.group('model')
        self.phone_dpi = mobj.group('dpi')
        self.phone_resolution = mobj.group('resolution')
        self.phone_chipset = mobj.group('chipset')

    @classmethod
    def generate_useragent(cls, **kwargs):
        """
        Helper method to generate a useragent string based on device parameters

        :param kwargs:
            - **app_version**
            - **android_version**
            - **android_release**
            - **brand**
            - **device**
            - **model**
            - **dpi**
            - **resolution**
            - **chipset**
        :return: A compatible user agent string
        """
        return Constants.USER_AGENT_FORMAT % {
            'app_version': kwargs.pop('app_version', None) or Constants.APP_VERSION,
            'android_version': int(kwargs.pop('android_version', None) or Constants.ANDROID_VERSION),
            'android_release': kwargs.pop('android_release', None) or Constants.ANDROID_RELEASE,
            'brand': kwargs.pop('phone_manufacturer', None) or Constants.PHONE_MANUFACTURER,
            'device': kwargs.pop('phone_device', None) or Constants.PHONE_DEVICE,
            'model': kwargs.pop('phone_model', None) or Constants.PHONE_MODEL,
            'dpi': kwargs.pop('phone_dpi', None) or Constants.PHONE_DPI,
            'resolution': kwargs.pop('phone_resolution', None) or Constants.PHONE_RESOLUTION,
            'chipset': kwargs.pop('phone_chipset', None) or Constants.PHONE_CHIPSET}

    @classmethod
    def validate_useragent(cls, value):
        """
        Helper method to validate a useragent string for format correctness

        :param value:
        :return:
        """
        mobj = re.search(Constants.USER_AGENT_EXPRESSION, value)
        if not mobj:
            raise ValueError('User-agent specified does not fit format required: %s' %
                             Constants.USER_AGENT_EXPRESSION)
        parse_params = {
            'app_version': mobj.group('app_version'),
            'android_version': int(mobj.group('android_version')),
            'android_release': mobj.group('android_release'),
            'brand': mobj.group('manufacturer'),
            'device': mobj.group('device'),
            'model': mobj.group('model'),
            'dpi': mobj.group('dpi'),
            'resolution': mobj.group('resolution'),
            'chipset': mobj.group('chipset')
        }
        return {
            'user_agent': Constants.USER_AGENT_FORMAT % parse_params,
            'parsed_params': parse_params
        }

    @property
    def csrftoken(self):
        """The client's current csrf token"""
        for cookie in self.cookie_jar:
            if cookie.name.lower() == 'csrftoken':
                return cookie.value
        return None

    @property
    def token(self):
        """For compatibility. Equivalent to csrftoken"""
        return self.csrftoken

    @property
    def authenticated_user_id(self):
        """The current authenticated user id"""
        for cookie in self.cookie_jar:
            if cookie.name.lower() == 'ds_user_id':
                return cookie.value
        return None

    @property
    def authenticated_user_name(self):
        """The current authenticated user name"""
        for cookie in self.cookie_jar:
            if cookie.name.lower() == 'ds_user':
                return cookie.value
        return None

    @property
    def rank_token(self):
        if not self.authenticated_user_id:
            return None
        return '%s_%s' % (self.authenticated_user_id, self.uuid)

    @property
    def authenticated_params(self):
        return {
            '_csrftoken': self.csrftoken,
            '_uuid': self.uuid,
            '_uid': self.authenticated_user_id
        }

    @property
    def cookie_jar(self):
        """The client's cookiejar instance."""
        return self.opener.cookie_jar

    @property
    def default_headers(self):
        return {
            'User-Agent': self.user_agent,
            'Connection': 'close',
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'X-IG-Capabilities': self.ig_capabilities,
            'X-IG-Connection-Type': 'WIFI',
        }

    def _generate_signature(self, input):
        return hmac.new(
            self.signature_key.encode('ascii'), input.encode('ascii'),
            digestmod=hashlib.sha256).hexdigest()

    @classmethod
    def generate_uuid(cls, return_hex=False, seed=None):
        """
        Generate uuid

        :param return_hex: Return in hex format
        :param seed: Seed value to generate a consistent uuid
        :return:
        """
        if seed:
            m = hashlib.md5()
            m.update(seed.encode('utf-8'))
            new_uuid = uuid.UUID(m.hexdigest())
        else:
            new_uuid = uuid.uuid1()
        if return_hex:
            return new_uuid.hex
        return str(new_uuid)

    @classmethod
    def generate_deviceid(cls, seed=None):
        """
        Generate an android device ID

        :param seed: Seed value to generate a consistent device ID
        :return:
        """
        return 'android-%s' % cls.generate_uuid(True, seed)[:16]

    def _read_response(self, response):
        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(response.read())
            res = gzip.GzipFile(fileobj=buf).read().decode('utf8')
        else:
            res = response.read().decode('utf8')
        return res

    def _call_api(self, endpoint, params=None, return_response=False, unsigned=False):
        url = self.api_url + endpoint
        headers = self.default_headers
        data = None
        if params or params == '':
            headers['Content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            if params == '':    # force post if empty string
                data = ''.encode('ascii')
            else:
                if not unsigned:
                    json_params = json.dumps(params)
                    hash_sig = self._generate_signature(json_params)
                    post_params = {
                        'ig_sig_key_version': self.key_version,
                        'signed_body': hash_sig + '.' + json_params
                    }
                else:
                    post_params = params
                data = urlencode(post_params).encode('ascii')

        req = Request(url, data, headers=headers)
        try:
            self.logger.debug('REQUEST: %s %s' % (url, req.get_method()))
            self.logger.debug('DATA: %s' % data)
            response = self.opener.open(req, timeout=self.timeout)
        except HTTPError as e:
            error_msg = e.reason
            error_response = e.read()
            self.logger.debug('RESPONSE: %s' % error_response)
            try:
                error_obj = json.loads(error_response)
                if error_obj.get('message') == 'login_required':
                    raise ClientLoginRequiredError(
                        error_obj.get('message'), code=e.code,
                        error_response=json.dumps(error_obj))
                elif error_obj.get('message'):
                    error_msg = '%s: %s' % (e.reason, error_obj['message'])
            except:
                # do nothing, prob can't parse json
                pass
            raise ClientError(error_msg, e.code, error_response)

        if return_response:
            return response

        response_content = self._read_response(response)
        self.logger.debug('RESPONSE: %s' % response_content)
        json_response = json.loads(response_content)

        if json_response.get('message', '') == 'login_required':
            raise ClientLoginRequiredError(
                json_response.get('message'),
                error_response=json.dumps(json_response))

        # not from oembed or an ok response
        if not json_response.get('provider_url') and json_response.get('status', '') != 'ok':
            raise ClientError(
                json_response.get('message', 'Unknown error'),
                error_response=json.dumps(json_response))

        return json_response

    def _validate_location(self, location):
        location_keys = ['external_source', 'name', 'address']
        if type(location) != dict:
            raise ValueError('Location must be a dict')

        # patch location object returned from location_search
        if 'external_source' not in location and 'external_id_source' in location and 'external_id' in location:
            external_source = location['external_id_source']
            location['external_source'] = external_source
            if external_source in self.EXTERNAL_LOC_SOURCES:
                location[self.EXTERNAL_LOC_SOURCES[external_source]] = location['external_id']
        for k in location_keys:
            if not location.get(k):
                raise ValueError('Location dict must contain "%s"' % k)
        for k, val in self.EXTERNAL_LOC_SOURCES.items():
            if location['external_source'] == k and not location.get(val):
                raise ValueError('Location dict must contain "%s"' % val)

        media_loc = {
            'name': location['name'],
            'address': location['lat'],
            'external_source': location['external_source'],
        }
        if 'lat' in location and 'lng' in location:
            media_loc['lat'] = location['lat']
            media_loc['lng'] = location['lng']
        for k, val in self.EXTERNAL_LOC_SOURCES.items():
            if location['external_source'] == k:
                media_loc['external_source'] = k
                media_loc[val] = location[val]
        return media_loc

    def login(self):
        """Login."""
        challenge_response = self._call_api(
            'si/fetch_headers/?' + urlencode({'challenge_type': 'signup', 'guid': self.generate_uuid(True)}),
            params='', return_response=True)
        cookie_info = challenge_response.info().get('Set-Cookie')
        mobj = re.search(r'csrftoken=(?P<csrf>[^;]+)', cookie_info)
        if not mobj:
            raise ClientError('Unable to get csrf from login challenge.')
        csrf = mobj.group('csrf')

        login_params = {
            'device_id': self.device_id,
            'guid': self.uuid,
            'phone_id': self.generate_uuid(return_hex=False, seed=self.device_id),
            '_csrftoken': csrf,
            'username': self.username,
            'password': self.password,
            'login_attempt_count': '0',
        }

        try:
            login_response = self._call_api(
                'accounts/login/', params=login_params, return_response=True)
        except HTTPError as e:
            error_response = e.read()
            if e.code == 400:
                raise ClientLoginError('Unable to login: %s' % e)
            raise ClientError(e.reason, e.code, error_response)

        if not self.csrftoken:
            raise ClientError('Unable to get csrf from login.')

        login_json = json.loads(self._read_response(login_response))

        if not login_json.get('logged_in_user', {}).get('pk'):
            raise ClientLoginError('Unable to login.')

        if self.on_login:
            on_login_callback = self.on_login
            on_login_callback(self)

        # # Post-login calls in client
        # self.sync()
        # self.autocomplete_user_list()
        # self.feed_timeline()
        # self.ranked_recipients()
        # self.recent_recipients()
        # self.direct_v2_inbox()
        # self.news_inbox()
        # self.explore()

    def logout(self):
        """Logout user"""
        endpoint = 'accounts/logout/'
        params = {
            'phone_id': self.generate_uuid(return_hex=False, seed=self.device_id),
            '_csrftoken': self.csrftoken,
            'guid': self.uuid,
            'device_id': self.device_id,
            '_uuid': self.uuid
        }
        return self._call_api(endpoint, params=params, unsigned=True)

    def sync(self, prelogin=False):
        """Synchronise experiments."""
        endpoint = 'qe/sync/'
        if prelogin:
            params = {
                'id': self.generate_uuid(),
                'experiments': Constants.LOGIN_EXPERIMENTS
            }
        else:
            params = {
                'id': self.authenticated_user_id,
                'experiments': Constants.EXPERIMENTS
            }
            params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def expose(self, experiment='ig_android_profile_contextual_feed'):
        endpoint = 'qe/expose/'
        params = {
            'id': self.authenticated_user_id,
            'experiment': experiment
        }
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def megaphone_log(self, log_type='feed_aysf', action='seen', reason='', **kwargs):
        """
        A tracking endpoint of sorts

        :param log_type:
        :param action:
        :param reason:
        :param kwargs:
        :return:
        """
        endpoint = 'megaphone/log/'
        params = {
            'type': log_type,
            'action': action,
            'reason': reason,
            '_uuid': self.uuid,
            'device_id': self.device_id,
            '_csrftoken': self.csrftoken,
            'uuid': self.generate_uuid(return_hex=True)
        }
        if kwargs:
            params.update(kwargs)
        return self._call_api(endpoint, params=params, unsigned=True)

    def current_user(self):
        """Get current user info"""
        endpoint = 'accounts/current_user/?edit=true'
        params = self.authenticated_params
        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def autocomplete_user_list(self):
        """User list for autocomplete"""
        endpoint = 'friendships/autocomplete_user_list/?' + urlencode({'followinfo': 'True', 'version': '2'})
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(user, drop_incompat_keys=self.drop_incompat_keys)
             for user in res['users']]
        return res

    def explore(self, **kwargs):
        """Get explore items"""
        query = {'is_prefetch': 'false', 'is_from_promote': 'false'}
        if kwargs:
            query.update(kwargs)
        res = self._call_api('discover/explore/?' + urlencode(query))
        if self.auto_patch:
            [ClientCompatPatch.media(item['media'], drop_incompat_keys=self.drop_incompat_keys)
             if item.get('media') else item for item in res['items']]
        return res

    def discover_channels_home(self):
        """Discover channels home"""
        endpoint = 'discover/channels_home/'
        res = self._call_api(endpoint)
        if self.auto_patch:
            for item in res.get('items', []):
                for row_item in item.get('row_items', []):
                    if row_item.get('media'):
                        ClientCompatPatch.media(row_item['media'])
        return res

    def discover_chaining(self, user_id):
        """
        Get suggested users

        :param user_id:
        :return:
        """
        endpoint = 'discover/chaining/?' + urlencode({'target_id': user_id})
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(user) for user in res.get('users', [])]
        return res

    def ranked_recipients(self):
        """Get ranked recipients"""
        res = self._call_api('direct_v2/ranked_recipients/?' + urlencode({'show_threads': 'true'}))
        return res

    def recent_recipients(self):
        """Get recent recipients"""
        res = self._call_api('direct_share/recent_recipients/')
        return res

    def news(self):
        """Get news"""
        return self._call_api('news/')

    def news_inbox(self):
        """Get news inbox"""
        return self._call_api('news/inbox/?' + urlencode({'limited_activity': 'true', 'show_su': 'true'}))

    def direct_v2_inbox(self):
        """Get v2 inbox"""
        return self._call_api('direct_v2/inbox/')

    def feed_liked(self):
        """Get liked feed"""
        res = self._call_api('feed/liked/')
        if self.auto_patch and res.get('items'):
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def user_info(self, user_id):
        """
        Get user info for a specified user id

        :param user_id:
        :return:
        """
        res = self._call_api('users/%(user_id)s/info/' % {'user_id': user_id})
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def username_info(self, user_name):
        """
        Get user info for a specified user name
        :param user_name:
        :return:
        """
        res = self._call_api('users/%(user_name)s/usernameinfo/' % {'user_name': user_name})
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def user_detail_info(self, user_id, **kwargs):
        """
        EXPERIMENTAL ENDPOINT, INADVISABLE TO USE.
        Get user detailed info

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
            - **min_timestamp**: For pagination
        :return:
        """
        endpoint = 'users/%(user_id)s/full_detail_info/' % {'user_id': user_id}
        if kwargs:
            endpoint += '?' + urlencode(kwargs)
        res = self._call_api(endpoint)
        if self.auto_patch:
            ClientCompatPatch.user(res['user_detail']['user'], drop_incompat_keys=self.drop_incompat_keys)
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('feed', {}).get('items', [])]
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('reel_feed', {}).get('items', [])]
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('user_story', {}).get('reel', {}).get('items', [])]
        return res

    def user_map(self, user_id):
        """
        Get a list of geo-tagged media from a user

        :param user_id: User id
        :return:
        """
        endpoint = 'maps/user/%(user_id)s/' % {'user_id': user_id}
        return self._call_api(endpoint)

    def feed_timeline(self):
        """Get timeline feed"""
        res = self._call_api('feed/timeline/')
        if self.auto_patch:
            [ClientCompatPatch.media(m['media_or_ad'], drop_incompat_keys=self.drop_incompat_keys)
             if m.get('media_or_ad') else m
             for m in res.get('feed_items', [])]
        return res

    def feed_popular(self):
        """Get popular feed"""
        endpoint = 'feed/popular/?' + urlencode({
            'people_teaser_supported': '1', 'rank_token': self.rank_token, 'ranked_content': 'true'})
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def media_info(self, media_id):
        """Get media info"""
        endpoint = 'media/%(media_id)s/info/' % {'media_id': media_id}
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def medias_info(self, media_ids):
        """
        Get multiple media infos

        :param media_ids: list of media ids
        :return:
        """
        if isinstance(media_ids, str):
            media_ids = [media_ids]

        endpoint = 'media/infos/'
        params = {
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken,
            'media_ids': ','.join(media_ids),
            'ranked_content': 'true'
        }
        res = self._call_api(endpoint, params=params, unsigned=True)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def media_permalink(self, media_id):
        """Get media permalink"""
        endpoint = 'media/%(media_id)s/permalink/' % {'media_id': media_id}
        res = self._call_api(endpoint)
        return res

    def media_comments(self, media_id, **kwargs):
        """
        Get media comments. Fixed at 20 comments returned per page.

        :param media_id: Media id
        :param kwargs:
            **max_id**: For pagination
        :return:
        """
        endpoint = 'media/%(media_id)s/comments/?' % {'media_id': media_id}
        if kwargs:
            endpoint += urlencode(kwargs)
        res = self._call_api(endpoint)

        if self.auto_patch:
            [ClientCompatPatch.comment(c, drop_incompat_keys=self.drop_incompat_keys)
             for c in res.get('comments', [])]
        return res

    def media_n_comments(self, media_id, n=150, reverse=False, **kwargs):
        """
        Helper method to retrieve n number of comments for a media id

        :param media_id: Media id
        :param n: Minimum number of comments to fetch
        :param reverse: Reverse list of comments (ordered by created_time)
        :param kwargs:
        :return:
        """

        endpoint = 'media/%(media_id)s/comments/?' % {'media_id': media_id}

        comments = []
        if kwargs:
            results = self._call_api(endpoint + urlencode(kwargs))
        else:
            results = self._call_api(endpoint)
        comments.extend(results.get('comments', []))
        while results.get('has_more_comments') and results.get('next_max_id') and len(comments) < n:
            kwargs.update({'max_id': results.get('next_max_id')})
            results = self._call_api(endpoint + urlencode(kwargs))
            comments.extend(results.get('comments', []))
            if not results.get('next_max_id') or not results.get('comments'):
                # bail out if no max_id or comments returned
                break

        if self.auto_patch:
            [ClientCompatPatch.comment(c, drop_incompat_keys=self.drop_incompat_keys)
             for c in comments]

        return sorted(comments, key=lambda k: k['created_time'], reverse=reverse)

    def edit_media(self, media_id, caption, usertags=[]):
        """
        Edit a media's caption

        :param media_id: Media id
        :param caption: Caption text
        :param usertags: array of user_ids and positions in the format below:

            .. code-block:: javascript

                usertags = [
                    {"user_id":4292127751, "position":[0.625347,0.4384531]}
                ]
        :return:
        """
        endpoint = 'media/%(media_id)s/edit_media/' % {'media_id': media_id}
        params = {'caption_text': caption}
        params.update(self.authenticated_params)
        if usertags:
            utags = {'in': [{'user_id': u['user_id'], 'position': u['position']} for u in usertags]}
            params['usertags'] = json.dumps(utags)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            ClientCompatPatch.media(res.get('media'))
        return res

    def delete_media(self, media_id):
        """
        Delete a media

        :param media_id: Media id
        :return:
            .. code-block:: javascript

                {"status": "ok", "did_delete": true}
        """
        endpoint = 'media/%(media_id)s/delete/' % {'media_id': media_id}
        params = {'media_id': media_id}
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def post_comment(self, media_id, comment_text):
        """
        Post a comment.
        Comment text validation according to https://www.instagram.com/developer/endpoints/comments/#post_media_comments

        :param media_id: Media id
        :param comment_text: Comment text
        :return:
            .. code-block:: javascript

                {
                  "comment": {
                    "status": "Active",
                    "media_id": 123456789,
                    "text": ":)",
                    "created_at": 1479453671.0,
                    "user": {
                      "username": "x",
                      "has_anonymous_profile_picture": false,
                      "profile_pic_url": "http://scontent-sit4-1.cdninstagram.com/abc.jpg",
                      "full_name": "x",
                      "pk": 123456789,
                      "is_verified": false,
                      "is_private": false
                    },
                    "content_type": "comment",
                    "created_at_utc": 1479482471,
                    "pk": 17865505612040669,
                    "type": 0
                  },
                  "status": "ok"
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

        endpoint = 'media/%(media_id)s/comment/' % {'media_id': media_id}
        params = {
            'comment_text': comment_text,
            'user_breadcrumb': gen_user_breadcrumb(len(comment_text)),
            'idempotence_token': self.generate_uuid(),
            'containermodule': 'comments_feed_timeline'
        }
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            ClientCompatPatch.comment(res['comment'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def delete_comment(self, media_id, comment_id):
        """
        Delete a comment

        :param media_id: Media id
        :param comment_id: Comment id
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(media_id)s/comment/%(comment_id)s/delete/' % {
            'media_id': media_id, 'comment_id': comment_id}
        params = {}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def media_likers(self, media_id):
        res = self._call_api('media/%(media_id)s/likers/' % {'media_id': media_id})
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def post_like(self, media_id):
        """
        Like a post

        :param media_id: Media id
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(media_id)s/like/' % {'media_id': media_id}
        params = {'media_id': media_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def delete_like(self, media_id):
        """
        Unlike a post

        :param media_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(media_id)s/unlike/' % {'media_id': media_id}
        params = {'media_id': media_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def user_feed(self, user_id, **kwargs):
        """
        Get the feed for the specified user id

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
            - **min_timestamp**: For pagination
        :return:
        """
        endpoint = 'feed/user/%(user_id)s/?' % {'user_id': user_id}
        default_params = {'rank_token': self.rank_token, 'ranked_content': 'true'}
        params = default_params.copy()
        if kwargs:
            params.update(kwargs)
        endpoint += urlencode(params)
        res = self._call_api(endpoint)

        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def username_feed(self, user_name, **kwargs):
        """
        Get the feed for the specified user name

        :param user_name:
        :param kwargs:
            - **max_id**: For pagination
            - **min_timestamp**: For pagination
        :return:
        """
        endpoint = 'feed/user/%(user_name)s/username/' % {'user_name': user_name}
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def user_following(self, user_id, **kwargs):
        """
        Get user followings

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        endpoint = 'friendships/%(user_id)s/following/?' % {'user_id': user_id}
        default_params = {
            'rank_token': self.rank_token,
        }
        params = default_params.copy()
        if kwargs:
            params.update(kwargs)
        endpoint += urlencode(params)
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def user_followers(self, user_id, **kwargs):
        """
        Get user followers

        :param user_id:
        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        endpoint = 'friendships/%(user_id)s/followers/?' % {'user_id': user_id}
        default_params = {
            'rank_token': self.rank_token,
        }
        params = default_params.copy()
        if kwargs:
            params.update(kwargs)
        endpoint += urlencode(params)
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def search_users(self, query, **kwargs):
        """
        Search users

        :param query: Search string
        :param kwargs:
            - **max_id**: For pagination
        :return:
        """
        endpoint = 'users/search/?'
        default_params = {
            'rank_token': self.rank_token,
            'ig_sig_key_version': self.key_version,
            'is_typeahead': 'true',
            'query': query
        }
        params = default_params.copy()
        if kwargs:
            params.update(kwargs)
        endpoint += urlencode(params)
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def oembed(self, url, **kwargs):
        """Get oembed info"""
        endpoint = 'oembed?'
        params = {'url': url}
        if kwargs:
            params.update(kwargs)
        endpoint += urlencode(params)
        res = self._call_api(endpoint)
        return res

    def reels_tray(self, **kwargs):
        """Get story reels tray"""
        endpoint = 'feed/reels_tray/'
        params = {}
        if kwargs or params:
            params.update(kwargs)
            endpoint += '?' + urlencode(params)

        res = self._call_api(endpoint)
        if self.auto_patch:
            for u in res.get('tray', []):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in u.get('items', [])]
        return res

    def user_reel_media(self, user_id, **kwargs):
        """
        Get user story/reel media

        :param user_id:
        :param kwargs:
        :return:
        """
        endpoint = 'feed/user/%(user_id)s/reel_media/' % {'user_id': user_id}
        params = {}
        if kwargs or params:
            params.update(kwargs)
            endpoint += '?' + urlencode(params)

        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def reels_media(self, user_ids, **kwargs):
        """
        Get multiple users' reel/story media

        :param user_ids: list of user IDs
        :param kwargs:
        :return:
        """
        endpoint = 'feed/reels_media/'
        user_ids = map(lambda x: str(x), user_ids)
        params = {'user_ids': user_ids}
        if kwargs:
            params.update(kwargs)

        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            for reel_media in res.get('reels_media', []):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in reel_media.get('items', [])]
            for user_id, reel in list(res.get('reels', {}).items()):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in reel.get('items', [])]
        return res

    def user_story_feed(self, user_id):
        """
        Get a user's story feed

        :param user_id:
        :return:
        """
        endpoint = 'feed/user/%(user_id)s/story/' % {'user_id': user_id}
        res = self._call_api(endpoint)
        if self.auto_patch and res.get('reel'):
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('reel', {}).get('items', [])]
        return res

    def media_seen(self, reels):
        """
        Mark multiple stories as seen

        :param reels: A dict of media_ids and timings

            .. code-block:: javascript

                {
                    "1309763051087626108_124317": "1470355944_1470372029",
                    "1309764045355643149_124317": "1470356063_1470372039",
                    "1309818450243415912_124317": "1470362548_1470372060",
                    "1309764653429046112_124317": "1470356135_1470372049",
                    "1309209597843679372_124317": "1470289967_1470372013"
                }

                where
                    1309763051087626108_124317 = <media_id>,
                    1470355944_1470372029 is <media_created_time>_<view_time>

        :return:
        """
        endpoint = 'media/seen/'
        params = {'nuxes': {}, 'reels': reels}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def friendships_pending(self):
        """Get pending follow requests"""
        res = self._call_api('friendships/pending/')
        if self.auto_patch and res.get('users'):
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def friendships_show(self, user_id):
        """
        Get friendship status with user id

        :param user_id:
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "incoming_request": false,
                    "is_blocking_reel": false,
                    "followed_by": false,
                    "is_muting_reel": false,
                    "outgoing_request": false,
                    "following": false,
                    "blocking": false,
                    "is_private": false
                }
        """
        endpoint = 'friendships/show/%(user_id)s/' % {'user_id': user_id}
        res = self._call_api(endpoint)
        return res

    def friendships_show_many(self, user_ids):
        """
        Get friendship status with mulitple user ids

        :param user_ids: list of user ids
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "friendship_statuses": {
                        "123456789": {
                            "following": false,
                            "incoming_request": true,
                            "outgoing_request": false,
                            "is_private": false
                        }
                    }
                }
        """
        if isinstance(user_ids, str):
            user_ids = [user_ids]

        endpoint = 'friendships/show_many/'
        params = {
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken,
            'user_ids': ','.join(user_ids)
        }
        res = self._call_api(endpoint, params=params, unsigned=True)
        return res

    def friendships_create(self, user_id):
        """
        Follow a user

        :param user_id: User id
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "friendship_status": {
                        "incoming_request": false,
                        "followed_by": false,
                        "outgoing_request": false,
                        "following": true,
                        "blocking": false,
                        "is_private": false
                    }
                }
        """
        endpoint = 'friendships/create/%(user_id)s/' % {'user_id': user_id}
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def friendships_destroy(self, user_id, **kwargs):
        """
        Unfollow a user

        :param user_id: User id
        :param kwargs:
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "incoming_request": false,
                    "is_blocking_reel": false,
                    "followed_by": false,
                    "is_muting_reel": false,
                    "outgoing_request": false,
                    "following": false,
                    "blocking": false,
                    "is_private": false
                }
        """
        endpoint = 'friendships/destroy/%(user_id)s/' % {'user_id': user_id}
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def friendships_block(self, user_id):
        """
        Block a user

        :param user_id: User id
        :return:
            .. code-block:: javascript

                {
                    "status": "ok",
                    "incoming_request": false,
                    "is_blocking_reel": false,
                    "followed_by": false,
                    "is_muting_reel": false,
                    "outgoing_request": false,
                    "following": false,
                    "blocking": true,
                    "is_private": false
                }
        """
        endpoint = 'friendships/block/%(user_id)s/' % {'user_id': user_id}
        params = {'user_id': user_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def translate(self, object_id, object_type):
        warnings.warn('This endpoint is not tested fully.', UserWarning)
        """type values:
            - 1 = CAPTION - unsupported
            - 2 = COMMENT - unsupported
            - 3 = BIOGRAPHY
        """
        endpoint = 'language/translate/' + '?' + urlencode({
            'id': object_id, 'type': object_type})
        res = self._call_api(endpoint)
        return res

    def bulk_translate(self, comment_ids):
        """
        Get translations of comments

        :param comment_ids: list of comment/caption IDs
        :return:
        """
        if isinstance(comment_ids, str):
            comment_ids = [comment_ids]

        endpoint = 'language/bulk_translate/'
        params = {'comment_ids': ','.join(comment_ids)}
        endpoint += '?' + urlencode(params)
        res = self._call_api(endpoint)
        return res

    def feed_tag(self, tag):
        """
        Get tag feed

        :param tag:
        :return:
        """
        endpoint = 'feed/tag/%(tag)s/' % {'tag': tag}
        res = self._call_api(endpoint)
        if self.auto_patch:
            if res.get('items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('items', [])]
            if res.get('ranked_items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('ranked_items', [])]
        return res

    def tag_info(self, tag):
        """
        Get tag info

        :param tag:
        :return:
        """
        endpoint = 'tags/%(tag)s/info/' % {'tag': tag}
        res = self._call_api(endpoint)
        return res

    def tag_related(self, tag):
        """
        Get related tags

        :param tag:
        :return:
        """
        endpoint = 'tags/%(tag)s/related/' % {'tag': tag}
        params = {
            'visited': json.dumps([{'id': tag, 'type': 'hashtag'}], separators=(',', ':')),
            'related_types': json.dumps(['hashtag'], separators=(',', ':'))}
        endpoint += '?' + urlencode(params)
        res = self._call_api(endpoint)
        return res

    def tag_search(self, text, **kwargs):
        """
        Search tag

        :param text:
        :param kwargs:
        :return:
        """
        endpoint = 'tags/search/'
        query = {
            'is_typeahead': True,
            'q': text,
            'rank_token': self.rank_token,
        }
        if kwargs:
            query.update(kwargs)
        endpoint += '?' + urlencode(query)
        res = self._call_api(endpoint)
        return res

    def usertag_feed(self, user_id, **kwargs):
        """
        Get a usertag feed

        :param user_id:
        :param kwargs:
        :return:
        """
        endpoint = 'usertags/%(user_id)s/feed/' % {'user_id': user_id}
        query = {'rank_token': self.rank_token, 'ranked_content': 'true'}
        if kwargs:
            query.update(kwargs)
        endpoint += '?' + urlencode(query)
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def usertag_self_remove(self, media_id):
        """
        Remove your own user tag from a media post

        :param media_id: Media id
        :return:
        """
        endpoint = 'usertags/%(media_id)s/remove/' % {'media_id': media_id}
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.media(res.get('media'))
        return res

    def feed_location(self, location_id):
        """
        Get a location feed

        :param location_id:
        :return:
        """
        endpoint = 'feed/location/%(location_id)s/' % {'location_id': location_id}
        res = self._call_api(endpoint)
        if self.auto_patch:
            if res.get('items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('items', [])]
            if res.get('ranked_items'):
                [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
                 for m in res.get('ranked_items', [])]
        return res

    def location_info(self, location_id):
        """
        Get a location info

        :param location_id:
        :return:
            .. code-block:: javascript

                {
                  "status": "ok",
                  "location": {
                    "external_source": "facebook_places",
                    "city": "",
                    "name": "Berlin Brandenburger Tor",
                    "facebook_places_id": 114849465334163,
                    "address": "Pariser Platz",
                    "lat": 52.51588,
                    "pk": 229573811,
                    "lng": 13.37892
                  }
                }
        """
        endpoint = 'locations/%(location_id)s/info/' % {'location_id': location_id}
        return self._call_api(endpoint)

    def location_related(self, location_id):
        """
        Get related locations

        :param location_id:
        :return:
        """
        endpoint = 'locations/%(location_id)s/related/' % {'location_id': location_id}
        params = {
            'visited': json.dumps([{'id': location_id, 'type': 'location'}], separators=(',', ':')),
            'related_types': json.dumps(['location'], separators=(',', ':'))}
        endpoint += '?' + urlencode(params)
        return self._call_api(endpoint)

    def location_search(self, latitude, longitude, query=None):
        """
        Location search

        :param latitude:
        :param longitude:
        :param query:
        :return:
        """
        endpoint = 'location_search/'
        params = {
            'rank_token': self.rank_token,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': int(time.time())
        }
        if query:
            params['search_query'] = query
        endpoint += '?' + urlencode(params)
        return self._call_api(endpoint)

    def location_fb_search(self, query):
        """
        Search for locations by query text

        :param query: search terms
        :return:
        """
        endpoint = 'fbsearch/places/?' + urlencode({'ranked_token': self.rank_token, 'query': query})
        res = self._call_api(endpoint)
        return res

    def discover_top_live(self):
        warnings.warn('This endpoint is not activated.', UserWarning)
        """Not enabled, returns 404"""
        endpoint = 'discover/top_live/'
        res = self._call_api(endpoint)
        return res

    def broadcast_info(self, broadcast_id):
        warnings.warn('This endpoint is not verified. Please do not use.', UserWarning)
        """UNCONFIRMED ENDPOINT - UNTESTED, DO NOT USE
        Possible Returns:
            - id
            - cover_frame_url
            - dash_playback_url
            - dash_abr_playback_url
            - broadcast_owner
            - viewer_count
            - published_time
            - muted
            - media_id
            - broadcast_status
            - ranked_position
            - seen_ranked_position
        """
        endpoint = 'live/%(broadcast_id)s/info/' % {'broadcast_id': broadcast_id}
        res = self._call_api(endpoint)
        return res

    def comment_like(self, comment_id):
        """
        Like a comment

        :param comment_id:

        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(comment_id)s/comment_like/' % {'comment_id': comment_id}
        params = self.authenticated_params
        return self._call_api(endpoint, params=params)

    def comment_unlike(self, comment_id):
        """
        Unlike a comment

        :param comment_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(comment_id)s/comment_unlike/' % {'comment_id': comment_id}
        params = self.authenticated_params
        return self._call_api(endpoint, params=params)

    def save_photo(self, media_id):
        """
        Save a photo

        :param media_id: Media id
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(media_id)s/save/' % {'media_id': media_id}
        params = {'radio_type': 'WIFI'}
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def unsave_photo(self, media_id):
        """
        Unsave a photo

        :param media_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(media_id)s/unsave/' % {'media_id': media_id}
        params = {'radio_type': 'WIFI'}
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def saved_feed(self):
        """
        Get saved photo feed

        :return:
        """
        endpoint = 'feed/saved/'
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.media(m['media'], drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', []) if m.get('media')]
        return res

    def edit_profile(self, first_name, biography, external_url, email, phone_number, gender):
        """
        Edit profile

        :param first_name:
        :param biography:
        :param external_url:
        :param email: Required.
        :param phone_number:
        :param gender: male: 1, female: 2, unspecified: 3
        :return:
        """
        if int(gender) not in [1, 2, 3]:
            raise ValueError('Invalid gender: %d' % int(gender))
        if not email:
            raise ValueError('Email is required.')

        endpoint = 'accounts/edit_profile/'
        params = {
            'username': self.authenticated_user_name,
            'gender': int(gender),
            'phone_number': phone_number or '',
            'first_name': first_name or '',
            'biography': biography or '',
            'external_url': external_url or '',
            'email': email,
        }
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            ClientCompatPatch.user(res.get('user'))
        return res

    def remove_profile_picture(self):
        """Remove profile picture"""
        endpoint = 'accounts/remove_profile_picture/'
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def change_profile_picture(self, photo_data):
        """
        Change profile picture

        :param photo_data: byte string of image
        :return:
        """
        endpoint = 'accounts/change_profile_picture/'
        json_params = json.dumps(self.authenticated_params)
        hash_sig = self._generate_signature(json_params)
        fields = [
            ('ig_sig_key_version', self.key_version),
            ('signed_body', hash_sig + '.' + json_params)
        ]
        files = [
            ('profile_pic', 'profile_pic', 'application/octet-stream', photo_data)
        ]

        content_type, body = MultipartFormDataEncoder(self.uuid).encode(fields, files)

        headers = self.default_headers
        headers['Content-Type'] = content_type
        headers['Content-Length'] = len(body)

        req = Request(self.api_url + endpoint, body, headers=headers)
        try:
            response = self.opener.open(req, timeout=self.timeout)
        except HTTPError as e:
            error_msg = e.reason
            error_response = e.read()
            try:
                error_obj = json.loads(error_response)
                if error_obj.get('message'):
                    error_msg = '%s: %s' % (e.reason, error_obj['message'])
            except:
                # do nothing, prob can't parse json
                pass
            raise ClientError(error_msg, e.code, error_response)

        json_response = json.loads(self._read_response(response))

        if self.auto_patch:
            ClientCompatPatch.user(json_response['user'], drop_incompat_keys=self.drop_incompat_keys)

        return json_response

    def set_account_private(self):
        """Make account private"""
        endpoint = 'accounts/set_private/'
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def set_account_public(self):
        """Make account public"""""
        endpoint = 'accounts/set_public/'
        res = self._call_api(endpoint, params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def disable_comments(self, media_id):
        """
        Disable comments for a media

        :param media_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/%(media_id)s/disable_comments/' % {'media_id': media_id}
        params = {
            '_csrftoken': self.csrftoken,
            '_uuid': self.uuid,
        }
        res = self._call_api(endpoint, params=params, unsigned=True)
        return res

    def enable_comments(self, media_id):
        """
        Enable comments for a media

        :param media_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """

        endpoint = 'media/%(media_id)s/enable_comments/' % {'media_id': media_id}
        params = {
            '_csrftoken': self.csrftoken,
            '_uuid': self.uuid,
        }
        res = self._call_api(endpoint, params=params, unsigned=True)
        return res

    @classmethod
    def standard_ratios(cls):
        """
        Acceptable min, max values of with/height ratios for an standard media upload

        :return: tuple of (min. ratio, max. ratio)
        """
        # Based on IG sampling
        # differs from https://help.instagram.com/1469029763400082
        # return 4.0/5.0, 1.19.0/1.0
        return 4.0 / 5.0, 90.0 / 47.0

    @classmethod
    def reel_ratios(cls):
        """
        Acceptable min, max values of with/height ratios for an story upload

        :return: tuple of (min. ratio, max. ratio)
        """
        # min_ratio = 9.0/16.0
        # max_ratio = 3.0/4.0 if is_video else 9.0/16.0
        device_ratios = [(3, 4), (2, 3), (5, 8), (3, 5), (9, 16), (10, 16), (40, 71)]
        aspect_ratios = map(lambda x: 1.0 * x[0] / x[1], device_ratios)
        return min(aspect_ratios), max(aspect_ratios)

    @classmethod
    def compatible_aspect_ratio(cls, size):
        """
        Helper method to check aspect ratio for standard uploads

        :param size: tuple of (width, height)
        :return: True/False
        """
        min_ratio, max_ratio = cls.standard_ratios()
        width, height = size
        this_ratio = 1.0 * width / height
        return min_ratio <= this_ratio <= max_ratio

    @classmethod
    def reel_compatible_aspect_ratio(cls, size, is_video=False):
        """
        Helper method to check aspect ratio for story uploads

        :param size: tuple of (width, height)
        :param is_video: True/False
        :return: True/False
        """
        min_ratio, max_ratio = cls.reel_ratios()
        width, height = size
        this_ratio = 1.0 * width / height
        return min_ratio <= this_ratio <= max_ratio

    def configure(self, upload_id, size, caption='', location=None):
        """
        Finalises a photo upload. This should not be called directly.

        :param upload_id:
        :param size: tuple of (width, height)
        :param caption:
        :param location: a dict of location information
        :return:
        """
        if not self.compatible_aspect_ratio(size):
            raise ClientError('Incompatible aspect ratio.')

        endpoint = 'media/configure/'
        width, height = size
        params = {
            'caption': caption,
            'media_folder': 'Instagram',
            'source_type': '4',
            'upload_id': upload_id,
            'device': {
                'manufacturer': self.phone_manufacturer,
                'model': self.phone_device,
                'android_version': self.android_version,
                'android_release': self.android_release
            },
            'edits': {
                'crop_original_size': [width * 1.0, height * 1.0],
                'crop_center': [0.0, -0.0],
                'crop_zoom': 1.0
            },
            'extra': {
                'source_width': width,
                'source_height': height,
            }
        }
        if location:
            media_loc = self._validate_location(location)
            params['location'] = json.dumps(media_loc)
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch and res.get('media'):
            ClientCompatPatch.media(res.get('media'), drop_incompat_keys=self.drop_incompat_keys)
        return res

    def configure_video(self, upload_id, size, duration, thumbnail_data, caption='', location=None):
        """
        Finalises a video upload. This should not be called directly.

        :param upload_id:
        :param size: tuple of (width, height)
        :param duration: in seconds
        :param thumbnail_data: byte string of thumbnail photo
        :param caption:
        :return:
        """
        if not self.compatible_aspect_ratio(size):
            raise ClientError('Incompatible aspect ratio.')

        self.post_photo(thumbnail_data, size, caption, upload_id, location=location)

        width, height = size
        endpoint = 'media/configure/?' + urlencode({'video': 1})
        params = {
            'upload_id': upload_id,
            'caption': caption,
            'source_type': '3',
            'poster_frame_index': 0,
            'length': 0.0,
            'audio_muted': False,
            'filter_type': '0',
            'video_result': 'deprecated',
            'clips': {
                'length': duration * 1.0,
                'source_type': '3',
                'camera_position': 'back'
            },
            'device': {
                'manufacturer': self.phone_manufacturer,
                'model': self.phone_device,
                'android_version': self.android_version,
                'android_release': self.android_release
            },
            'extra': {
                'source_width': width,
                'source_height': height
            }
        }
        if location:
            media_loc = self._validate_location(location)
            params['location'] = json.dumps(media_loc)
            if 'lat' in location and 'lng' in location:
                params['geotag_enabled'] = '1'
                params['av_latitude'] = '0.0'
                params['av_longitude'] = '0.0'
                params['posting_latitude'] = str(location['lat'])
                params['posting_longitude'] = str(location['lng'])
                params['media_latitude'] = str(location['lat'])
                params['media_latitude'] = str(location['lng'])

        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if res.get('media') and self.auto_patch:
            ClientCompatPatch.media(res.get('media'), drop_incompat_keys=self.drop_incompat_keys)
        return res

    def configure_to_reel(self, upload_id, size):
        """
        Finalises a photo story upload. This should not be called directly.

        :param upload_id:
        :param size: tuple of (width, height)
        :return:
        """
        if not self.reel_compatible_aspect_ratio(size, is_video=False):
            raise ClientError('Incompatible aspect ratio.')

        endpoint = 'media/configure_to_reel/'
        width, height = size
        params = {
            'source_type': '3',
            'upload_id': upload_id,
            'device': {
                'manufacturer': self.phone_manufacturer,
                'model': self.phone_device,
                'android_version': self.android_version,
                'android_release': self.android_release
            },
            'edits': {
                'crop_original_size': [width * 1.0, height * 1.0],
                'crop_center': [0.0, 0.0],
                'crop_zoom': 1.3333334
            },
            'extra': {
                'source_width': width,
                'source_height': height,
            }
        }
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch and res.get('media'):
            ClientCompatPatch.media(res.get('media'), drop_incompat_keys=self.drop_incompat_keys)
        return res

    def configure_video_to_reel(self, upload_id, size, duration, thumbnail_data):
        """
        Finalises a video story upload. This should not be called directly.

        :param upload_id:
        :param size: tuple of (width, height)
        :return:
        """
        if not self.reel_compatible_aspect_ratio(size, is_video=True):
            raise ClientError('Incompatible aspect ratio.')

        res = self.post_photo(thumbnail_data, size, '', upload_id=upload_id, to_reel=True)

        endpoint = 'media/configure_to_reel/?' + urlencode({'video': '1'})
        width, height = size
        params = {
            'source_type': '3',
            'upload_id': upload_id,
            'poster_frame_index': 0,
            'length': duration * 1.0,
            'audio_muted': False,
            'filter_type': '0',
            'video_result': 'deprecated',
            'clips': {
                'length': duration * 1.0,
                'source_type': '3',
                'camera_position': 'back'
            },
            'device': {
                'manufacturer': self.phone_manufacturer,
                'model': self.phone_device,
                'android_version': self.android_version,
                'android_release': self.android_release
            },
            'extra': {
                'source_width': width,
                'source_height': height,
            },
        }

        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch and res.get('media'):
            ClientCompatPatch.media(res.get('media'), drop_incompat_keys=self.drop_incompat_keys)
        return res

    def post_photo(self, photo_data, size, caption='', upload_id=None, to_reel=False, **kwargs):
        """
        Upload a photo.

        [TODO] FLAKY, IG is very finicky about sizes, etc, needs testing.

        :param photo_data: byte string of the image
        :param size: tuple of (width, height)
        :param caption:
        :param upload_id:
        :param to_reel: a Story photo
        :param kwargs:
            - **location**: a dict of venue/location information, from location_search() or location_fb_search()
        :return:
        """
        warnings.warn('This endpoint has not been fully tested.', UserWarning)

        # if upload_id is provided, it's a thumbnail for a vid upload
        for_video = True if upload_id else False

        if not for_video:
            if not to_reel and not self.compatible_aspect_ratio(size):
                raise ClientError('Incompatible aspect ratio.')
            if to_reel and not self.reel_compatible_aspect_ratio(size, is_video=True):
                raise ClientError('Incompatible reel aspect ratio.')

        location = kwargs.pop('location', None)
        if location:
            self._validate_location(location)

        if not upload_id:
            upload_id = str(int(time.time() * 1000))

        endpoint = 'upload/photo/'
        fields = [
            ('upload_id', upload_id),
            ('_uuid', self.uuid),
            ('_csrftoken', self.csrftoken),
            ('image_compression', '{"lib_name":"jt","lib_version":"1.3.0","quality":"87"}')
        ]
        files = [
            ('photo', 'pending_media_%s%s' % (str(int(time.time() * 1000)), '.jpg'),
             'application/octet-stream', photo_data)
        ]

        content_type, body = MultipartFormDataEncoder(self.uuid).encode(fields, files)
        headers = self.default_headers
        headers['Content-Type'] = content_type
        headers['Content-Length'] = len(body)

        req = Request(self.api_url + endpoint, body, headers=headers)
        try:
            response = self.opener.open(req, timeout=self.timeout)
        except HTTPError as e:
            error_msg = e.reason
            error_response = e.read()
            try:
                error_obj = json.loads(error_response)
                if error_obj.get('message'):
                    error_msg = '%s: %s' % (e.reason, error_obj['message'])
            except:
                # do nothing, prob can't parse json
                pass
            raise ClientError(error_msg, e.code, error_response)

        json_response = json.loads(self._read_response(response))

        upload_id = json_response['upload_id']

        # # NOTES: Logging traffic doesn't seem to indicate any additional "configure" after upload
        # # BUT not doing a "configure" causes a video post to fail with a
        # # "Other media configure error: b'yEmZkUpAj4'" error
        # if for_video:
        #     logger.debug('Skip photo configure.')
        #     return json_response

        if to_reel:
            return self.configure_to_reel(upload_id, size)
        else:
            return self.configure(upload_id, size, caption=caption, location=location)

    def post_video(self, video_data, size, duration, thumbnail_data, caption='', to_reel=False, **kwargs):
        """
        Upload a video

        [TODO] FLAKY, IG is very picky about sizes, etc, needs testing.

        :param video_data: byte string of the video content
        :param size: tuple of (width, height)
        :param duration: in seconds
        :param thumbnail_data: byte string of the video thumbnail content
        :param caption:
        :param to_reel: post to reel as Story
        :param kwargs:
             - **location**: a dict of venue/location information, from location_search() or location_fb_search()
        :return:
        """
        warnings.warn('This endpoint has not been fully tested.', UserWarning)

        if not to_reel and not self.compatible_aspect_ratio(size):
            raise ClientError('Incompatible aspect ratio.')

        if to_reel and not self.reel_compatible_aspect_ratio(size, is_video=True):
            raise ClientError('Incompatible reel aspect ratio.')

        location = kwargs.pop('location', None)
        if location:
            self._validate_location(location)

        endpoint = 'upload/video/'
        upload_id = str(int(time.time() * 1000))
        width, height = size
        params = {
            '_csrftoken': self.csrftoken,
            '_uuid': self.uuid,
            'upload_id': upload_id,
            'media_type': '2',
            'upload_media_duration_ms': int(duration * 1000),
            'upload_media_width': width,
            'upload_media_height': height,
        }

        res = self._call_api(endpoint, params=params, unsigned=True)
        upload_url = res['video_upload_urls'][-1]['url']
        upload_job = res['video_upload_urls'][-1]['job']

        chunk_count = 4
        total_len = len(video_data)

        # Alternatively, can use max_chunk_size_generator(20480, video_data)
        # [TODO] We can be a little smart about using either generators
        # depending on the file size, or other factors
        for chunk, data in max_chunk_count_generator(chunk_count, video_data):
            headers = self.default_headers
            headers['Connection'] = 'keep-alive'
            headers['Content-Type'] = 'application/octet-stream'
            headers['Content-Disposition'] = 'attachment; filename="video.mov"'
            headers['Session-ID'] = upload_id
            headers['job'] = upload_job
            headers['Content-Length'] = chunk.length
            headers['Content-Range'] = 'bytes %d-%d/%d' % (chunk.start, chunk.end - 1, total_len)
            self.logger.debug('Uploading Content-Range: %s' % headers['Content-Range'])

            req = Request(
                upload_url.encode('utf-8'), data=data, headers=headers)

            try:
                res = self.opener.open(req, timeout=self.timeout)
                if chunk.is_last and res.info().get('Content-Type') == 'application/json':
                    # last chunk
                    upload_res = json.loads(self._read_response(res))

                    configure_delay = int(upload_res.get('configure_delay_ms', 0)) / 1000.0
                    self.logger.debug('Configure delay: %s' % configure_delay)
                    time.sleep(configure_delay)

            except HTTPError as e:
                error_msg = e.reason
                error_response = e.read()
                try:
                    error_obj = json.loads(error_response)
                    if error_obj.get('message'):
                        error_msg = '%s: %s' % (e.reason, error_obj['message'])
                except:
                    # do nothing, prob can't parse json
                    pass
                raise ClientError(error_msg, e.code, error_response)

        if not to_reel:
            return self.configure_video(
                upload_id, size, duration, thumbnail_data, caption=caption, location=location)
        else:
            return self.configure_video_to_reel(upload_id, size, duration, thumbnail_data)
