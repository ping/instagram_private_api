# Copyright (c) 2017 https://github.com/ping
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

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
from socket import timeout, error as SocketError
from ssl import SSLError
from .compat import (
    compat_urllib_parse, compat_urllib_error,
    compat_urllib_request, compat_urllib_parse_urlparse,
    compat_http_client)
from .errors import (
    ErrorHandler, ClientError,
    ClientLoginRequiredError, ClientCookieExpiredError,
    ClientConnectionError
)
try:  # Python 3:
    # Not a no-op, we're adding this to the namespace so it can be imported.
    ConnectionError = ConnectionError       # pylint: disable=redefined-builtin
except NameError:  # Python 2:
    class ConnectionError(Exception):
        pass

from .constants import Constants
from .http import ClientCookieJar
from .endpoints import (
    AccountsEndpointsMixin, DiscoverEndpointsMixin, FeedEndpointsMixin,
    FriendshipsEndpointsMixin, LiveEndpointsMixin, MediaEndpointsMixin,
    MiscEndpointsMixin, LocationsEndpointsMixin, TagsEndpointsMixin,
    UsersEndpointsMixin, UploadEndpointsMixin, UsertagsEndpointsMixin,
    CollectionsEndpointsMixin, HighlightsEndpointsMixin,
    IGTVEndpointsMixin,
    ClientDeprecationWarning, ClientPendingDeprecationWarning,
    ClientExperimentalWarning
)

logger = logging.getLogger(__name__)
# Force Client deprecation warnings to always appear
warnings.simplefilter('always', ClientDeprecationWarning)
warnings.simplefilter('always', ClientPendingDeprecationWarning)
warnings.simplefilter('default', ClientExperimentalWarning)


class Client(AccountsEndpointsMixin, DiscoverEndpointsMixin, FeedEndpointsMixin,
             FriendshipsEndpointsMixin, LiveEndpointsMixin, MediaEndpointsMixin,
             MiscEndpointsMixin, LocationsEndpointsMixin, TagsEndpointsMixin,
             UsersEndpointsMixin, UploadEndpointsMixin, UsertagsEndpointsMixin,
             CollectionsEndpointsMixin, HighlightsEndpointsMixin,
             IGTVEndpointsMixin, object):
    """Main API client class for the private app api."""

    API_URL = 'https://i.instagram.com/api/{version!s}/'

    USER_AGENT = Constants.USER_AGENT
    IG_SIG_KEY = Constants.IG_SIG_KEY
    IG_CAPABILITIES = Constants.IG_CAPABILITIES
    SIG_KEY_VERSION = Constants.SIG_KEY_VERSION
    APPLICATION_ID = Constants.APPLICATION_ID

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
            - **proxy_handler**: Specify your own proxy handler
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
        # application session ID
        self.session_id = (
            kwargs.pop('session_id', None) or user_settings.get('session_id') or
            self.generate_uuid(False))
        self.signature_key = (
            kwargs.pop('signature_key', None) or user_settings.get('signature_key') or
            self.IG_SIG_KEY)
        self.key_version = (
            kwargs.pop('key_version', None) or user_settings.get('key_version') or
            self.SIG_KEY_VERSION)
        self.ig_capabilities = (
            kwargs.pop('ig_capabilities', None) or user_settings.get('ig_capabilities') or
            self.IG_CAPABILITIES)
        self.application_id = (
            kwargs.pop('application_id', None) or user_settings.get('application_id') or
            self.APPLICATION_ID)

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
            self.version_code = (
                kwargs.pop('version_code', None) or user_settings.get('version_code') or
                Constants.VERSION_CODE)

        cookie_string = kwargs.pop('cookie', None) or user_settings.get('cookie')
        cookie_jar = ClientCookieJar(cookie_string=cookie_string)
        if cookie_string and cookie_jar.auth_expires and int(time.time()) >= cookie_jar.auth_expires:
            raise ClientCookieExpiredError('Cookie expired at {0!s}'.format(cookie_jar.auth_expires))
        cookie_handler = compat_urllib_request.HTTPCookieProcessor(cookie_jar)

        proxy_handler = kwargs.pop('proxy_handler', None)
        if not proxy_handler:
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

        # Allow user to override custom ssl context where possible
        custom_ssl_context = kwargs.pop('custom_ssl_context', None)
        try:
            https_handler = compat_urllib_request.HTTPSHandler(context=custom_ssl_context)
        except TypeError:
            # py version < 2.7.9
            https_handler = compat_urllib_request.HTTPSHandler()

        handlers.extend([
            compat_urllib_request.HTTPHandler(),
            https_handler,
            cookie_handler])
        opener = compat_urllib_request.build_opener(*handlers)
        opener.cookie_jar = cookie_jar
        self.opener = opener

        # ad_id must be initialised after cookie_jar/opener because
        # it relies on self.authenticated_user_name
        self.ad_id = (
            kwargs.pop('ad_id', None) or user_settings.get('ad_id') or
            self.generate_adid())

        if not cookie_string:   # [TODO] There's probably a better way than to depend on cookie_string
            if not self.username or not self.password:
                raise ClientLoginRequiredError('login_required', code=400)
            self.login()

        self.logger.debug('USERAGENT: {0!s}'.format(self.user_agent))
        super(Client, self).__init__()

    @property
    def settings(self):
        """Helper property that extracts the settings that you should cache
        in addition to username and password."""
        return {
            'uuid': self.uuid,
            'device_id': self.device_id,
            'ad_id': self.ad_id,
            'session_id': self.session_id,
            'cookie': self.cookie_jar.dump(),
            'created_ts': int(time.time())
        }

    @property
    def user_agent(self):
        """Returns the useragent string that the client is currently using."""
        return Constants.USER_AGENT_FORMAT.format(**{
            'app_version': self.app_version,
            'android_version': self.android_version,
            'android_release': self.android_release,
            'brand': self.phone_manufacturer,
            'device': self.phone_device,
            'model': self.phone_model,
            'dpi': self.phone_dpi,
            'resolution': self.phone_resolution,
            'chipset': self.phone_chipset,
            'version_code': self.version_code})

    @user_agent.setter
    def user_agent(self, value):
        """Override the useragent string with your own"""
        mobj = re.search(Constants.USER_AGENT_EXPRESSION, value)
        if not mobj:
            raise ValueError('User-agent specified does not fit format required: {0!s}'.format(
                Constants.USER_AGENT_EXPRESSION))
        self.app_version = mobj.group('app_version')
        self.android_release = mobj.group('android_release')
        self.android_version = int(mobj.group('android_version'))
        self.phone_manufacturer = mobj.group('manufacturer')
        self.phone_device = mobj.group('device')
        self.phone_model = mobj.group('model')
        self.phone_dpi = mobj.group('dpi')
        self.phone_resolution = mobj.group('resolution')
        self.phone_chipset = mobj.group('chipset')
        self.version_code = mobj.group('version_code')

    @staticmethod
    def generate_useragent(**kwargs):
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
        return Constants.USER_AGENT_FORMAT.format(**{
            'app_version': kwargs.pop('app_version', None) or Constants.APP_VERSION,
            'android_version': int(kwargs.pop('android_version', None) or Constants.ANDROID_VERSION),
            'android_release': kwargs.pop('android_release', None) or Constants.ANDROID_RELEASE,
            'brand': kwargs.pop('phone_manufacturer', None) or Constants.PHONE_MANUFACTURER,
            'device': kwargs.pop('phone_device', None) or Constants.PHONE_DEVICE,
            'model': kwargs.pop('phone_model', None) or Constants.PHONE_MODEL,
            'dpi': kwargs.pop('phone_dpi', None) or Constants.PHONE_DPI,
            'resolution': kwargs.pop('phone_resolution', None) or Constants.PHONE_RESOLUTION,
            'chipset': kwargs.pop('phone_chipset', None) or Constants.PHONE_CHIPSET,
            'version_code': kwargs.pop('version_code', None) or Constants.VERSION_CODE})

    @staticmethod
    def validate_useragent(value):
        """
        Helper method to validate a useragent string for format correctness

        :param value:
        :return:
        """
        mobj = re.search(Constants.USER_AGENT_EXPRESSION, value)
        if not mobj:
            raise ValueError(
                'User-agent specified does not fit format required: {0!s}'.format(
                    Constants.USER_AGENT_EXPRESSION))
        parse_params = {
            'app_version': mobj.group('app_version'),
            'android_version': int(mobj.group('android_version')),
            'android_release': mobj.group('android_release'),
            'brand': mobj.group('manufacturer'),
            'device': mobj.group('device'),
            'model': mobj.group('model'),
            'dpi': mobj.group('dpi'),
            'resolution': mobj.group('resolution'),
            'chipset': mobj.group('chipset'),
            'version_code': mobj.group('version_code'),
        }
        return {
            'user_agent': Constants.USER_AGENT_FORMAT.format(**parse_params),
            'parsed_params': parse_params
        }

    def get_cookie_value(self, key, domain=''):
        now = int(time.time())
        eternity = now + 100 * 365 * 24 * 60 * 60   # future date for non-expiring cookies
        if not domain:
            domain = compat_urllib_parse_urlparse(self.API_URL).netloc

        for cookie in sorted(
                self.cookie_jar, key=lambda c: c.expires or eternity, reverse=True):
            # don't return expired cookie
            if cookie.expires and cookie.expires < now:
                continue
            # cookie domain may be i.instagram.com or .instagram.com
            cookie_domain = cookie.domain
            # simple domain matching
            if cookie_domain.startswith('.'):
                cookie_domain = cookie_domain[1:]
            if not domain.endswith(cookie_domain):
                continue

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
        return self.get_cookie_value('ds_user_id')

    @property
    def authenticated_user_name(self):
        """The current authenticated user name"""
        return self.get_cookie_value('ds_user')

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
        return '{0!s}_{1!s}'.format(self.authenticated_user_id, self.uuid)

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
            'X-IG-Connection-Speed': '{0:d}kbps'.format(random.randint(1000, 5000)),
            'X-IG-App-ID': self.application_id,
            'X-IG-Bandwidth-Speed-KBPS': '-1.000',
            'X-IG-Bandwidth-TotalBytes-B': '0',
            'X-IG-Bandwidth-TotalTime-MS': '0',
            'X-FB-HTTP-Engine': Constants.FB_HTTP_ENGINE,
        }

    @property
    def radio_type(self):
        """For use in certain endpoints"""
        return 'wifi-none'

    def _generate_signature(self, data):
        """
        Generates the signature for a data string

        :param data: content to be signed
        :return:
        """
        return hmac.new(
            self.signature_key.encode('ascii'), data.encode('ascii'),
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
        return 'android-{0!s}'.format(cls.generate_uuid(True, seed)[:16])

    def generate_adid(self, seed=None):
        """
        Generate an Advertising ID based on the login username since
        the Google Ad ID is a personally identifying but resettable ID.

        :return:
        """
        modified_seed = seed or self.authenticated_user_name or self.username
        if modified_seed:
            # Do some trivial mangling of original seed
            sha2 = hashlib.sha256()
            sha2.update(modified_seed.encode('utf-8'))
            modified_seed = sha2.hexdigest()
        return self.generate_uuid(False, modified_seed)

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

    def _call_api(self, endpoint, params=None, query=None, return_response=False, unsigned=False, version='v1'):
        """
        Calls the private api.

        :param endpoint: endpoint path that should end with '/', example 'discover/explore/'
        :param params: POST parameters
        :param query: GET url query parameters
        :param return_response: return the response instead of the parsed json object
        :param unsigned: use post params as-is without signing
        :param version: for the versioned api base url. Default 'v1'.
        :return:
        """
        url = '{0}{1}'.format(self.api_url.format(version=version), endpoint)
        if query:
            url += ('?' if '?' not in endpoint else '&') + compat_urllib_parse.urlencode(query)

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
                    # direct form post
                    post_params = params
                data = compat_urllib_parse.urlencode(post_params).encode('ascii')

        req = compat_urllib_request.Request(url, data, headers=headers)
        try:
            self.logger.debug('REQUEST: {0!s} {1!s}'.format(url, req.get_method()))
            self.logger.debug('DATA: {0!s}'.format(data))
            response = self.opener.open(req, timeout=self.timeout)
        except compat_urllib_error.HTTPError as e:
            error_response = self._read_response(e)
            self.logger.debug('RESPONSE: {0:d} {1!s}'.format(e.code, error_response))
            ErrorHandler.process(e, error_response)

        except (SSLError, timeout, SocketError,
                compat_urllib_error.URLError,   # URLError is base of HTTPError
                compat_http_client.HTTPException,
                ConnectionError) as connection_error:
            raise ClientConnectionError('{} {}'.format(
                connection_error.__class__.__name__, str(connection_error)))

        if return_response:
            return response

        response_content = self._read_response(response)
        self.logger.debug('RESPONSE: {0:d} {1!s}'.format(response.code, response_content))
        json_response = json.loads(response_content)

        if json_response.get('message', '') == 'login_required':
            raise ClientLoginRequiredError(
                json_response.get('message'), code=response.code,
                error_response=json.dumps(json_response))

        # not from oembed or an ok response
        if not json_response.get('provider_url') and json_response.get('status', '') != 'ok':
            raise ClientError(
                json_response.get('message', 'Unknown error'), code=response.code,
                error_response=json.dumps(json_response))

        return json_response
