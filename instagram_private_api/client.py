# -*- coding: utf-8 -*-

import logging
import hmac
import hashlib
import uuid
import json
import re
import time
import random
from datetime import datetime
import gzip
from io import BytesIO
import warnings
from .compat import compat_urllib_parse
from .compat import compat_urllib_error
from .compat import compat_urllib_request
from .compat import compat_urllib_parse_urlparse
from .errors import ClientError, ClientLoginError, ClientLoginRequiredError, ClientCookieExpiredError
from .constants import Constants
from .http import ClientCookieJar
from .endpoints.accounts import AccountsEndpointsMixin
from .endpoints.discover import DiscoverEndpointsMixin
from .endpoints.feed import FeedEndpointsMixin
from .endpoints.friendships import FriendshipsEndpointsMixin
from .endpoints.live import LiveEndpointsMixin
from .endpoints.media import MediaEndpointsMixin
from .endpoints.misc import MiscEndpointsMixin
from .endpoints.locations import LocationsEndpointsMixin
from .endpoints.tags import TagsEndpointsMixin
from .endpoints.upload import UploadEndpointsMixin
from .endpoints.users import UsersEndpointsMixin
from .endpoints.usertags import UsertagsEndpointsMixin

logger = logging.getLogger(__name__)


class Client(AccountsEndpointsMixin, DiscoverEndpointsMixin, FeedEndpointsMixin,
             FriendshipsEndpointsMixin, LiveEndpointsMixin, MediaEndpointsMixin,
             MiscEndpointsMixin, LocationsEndpointsMixin, TagsEndpointsMixin,
             UsersEndpointsMixin, UploadEndpointsMixin, UsertagsEndpointsMixin,
             object):

    API_URL = 'https://i.instagram.com/api/v1/'

    USER_AGENT = Constants.USER_AGENT
    IG_SIG_KEY = Constants.IG_SIG_KEY
    IG_CAPABILITIES = Constants.IG_CAPABILITIES
    SIG_KEY_VERSION = Constants.SIG_KEY_VERSION

    def __init__(self, username, password, **kwargs):
        """

        :param username: Login username
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
            kwargs.pop('ig_capabilities', None) or user_settings.get('ig_capabilities') or
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
        cookie_handler = compat_urllib_request.HTTPCookieProcessor(cookie_jar)

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
                raise ClientError('Invalid proxy argument: %s' % proxy)
        handlers = []
        if proxy_handler:
            handlers.append(proxy_handler)
        try:
            httpshandler = compat_urllib_request.HTTPSHandler(context=custom_ssl_context)
        except TypeError as e:
            # py version < 2.7.9
            httpshandler = compat_urllib_request.HTTPSHandler()

        handlers.extend([
            compat_urllib_request.HTTPHandler(),
            httpshandler,
            cookie_handler])
        opener = compat_urllib_request.build_opener(*handlers)
        opener.cookie_jar = cookie_jar
        self.opener = opener

        if not cookie_string:   # or not self.token or not self.rank_token:
            if not self.username or not self.password:
                raise ClientLoginRequiredError('login_required', code=400)
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
    def token(self):
        """For compatibility. Equivalent to :meth:`csrftoken`"""
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
    def phone_id(self):
        """Current phone ID. For use in certain functions."""
        return self.generate_uuid(return_hex=False, seed=self.device_id)

    @property
    def timezone_offset(self):
        """Timezone offset in seconds. For use in certain functions."""
        return int(round((datetime.now() - datetime.utcnow()).total_seconds()))

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
            'X-IG-Connection-Speed': '%dkbps' % random.randint(1000, 5000),
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
                    json_params = json.dumps(params, separators=(',', ':'))
                    hash_sig = self._generate_signature(json_params)
                    post_params = {
                        'ig_sig_key_version': self.key_version,
                        'signed_body': hash_sig + '.' + json_params
                    }
                else:
                    post_params = params
                data = compat_urllib_parse.urlencode(post_params).encode('ascii')

        req = compat_urllib_request.Request(url, data, headers=headers)
        try:
            self.logger.debug('REQUEST: %s %s' % (url, req.get_method()))
            self.logger.debug('DATA: %s' % data)
            response = self.opener.open(req, timeout=self.timeout)
        except compat_urllib_error.HTTPError as e:
            error_msg = e.reason
            error_response = e.read()
            self.logger.debug('RESPONSE: %d %s' % (e.code, error_response))
            try:
                error_obj = json.loads(error_response)
                if error_obj.get('message') == 'login_required':
                    raise ClientLoginRequiredError(
                        error_obj.get('message'), code=e.code,
                        error_response=json.dumps(error_obj))
                elif error_obj.get('message'):
                    error_msg = '%s: %s' % (e.reason, error_obj['message'])
            except (ClientLoginError, ClientLoginRequiredError):
                raise
            except:
                # do nothing, prob can't parse json
                pass
            raise ClientError(error_msg, e.code, error_response)

        if return_response:
            return response

        response_content = self._read_response(response)
        self.logger.debug('RESPONSE: %d %s' % (response.code, response_content))
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

    def login(self):
        """Login."""
        challenge_response = self._call_api(
            'si/fetch_headers/?' + compat_urllib_parse.urlencode(
                {'challenge_type': 'signup', 'guid': self.generate_uuid(True)}),
            params='', return_response=True)
        cookie_info = challenge_response.info().get('Set-Cookie')
        mobj = re.search(r'csrftoken=(?P<csrf>[^;]+)', cookie_info)
        if not mobj:
            raise ClientError('Unable to get csrf from login challenge.')
        csrf = mobj.group('csrf')

        login_params = {
            'device_id': self.device_id,
            'guid': self.uuid,
            'phone_id': self.phone_id,
            '_csrftoken': csrf,
            'username': self.username,
            'password': self.password,
            'login_attempt_count': '0',
        }

        try:
            login_response = self._call_api(
                'accounts/login/', params=login_params, return_response=True)
        except compat_urllib_error.HTTPError as e:
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
