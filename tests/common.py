# flake8: noqa
import unittest
import time
import codecs
try:
    import unittest.mock as compat_mock
except ImportError:
    import mock as compat_mock
import sys
import os
try:
    from instagram_private_api import (
        __version__, Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientThrottledError, ClientCompatPatch,
        ClientLoginRequiredError, MediaTypes,
        ClientSentryBlockError, ClientCheckpointRequiredError,
        ClientChallengeRequiredError)
    from instagram_private_api.utils import (
        InstagramID, gen_user_breadcrumb,
        max_chunk_size_generator, max_chunk_count_generator, get_file_size,
        ig_chunk_generator
    )   # noqa
    from instagram_private_api.constants import Constants
    from instagram_private_api.compat import compat_urllib_parse
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        __version__, Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientThrottledError, ClientCompatPatch,
        ClientLoginRequiredError, MediaTypes,
        ClientSentryBlockError, ClientCheckpointRequiredError,
        ClientChallengeRequiredError)
    from instagram_private_api.utils import (
        InstagramID, gen_user_breadcrumb,
        max_chunk_size_generator, max_chunk_count_generator, get_file_size,
        ig_chunk_generator
    )   # noqa
    from instagram_private_api.constants import Constants
    from instagram_private_api.compat import compat_urllib_parse

try:
    from instagram_web_api import (
        __version__ as __webversion__,
        Client as WebClient,
        ClientError as WebClientError,
        ClientLoginError as WebClientLoginError,
        ClientCookieExpiredError as WebClientCookieExpiredError,
        ClientCompatPatch as WebClientCompatPatch)
    from instagram_web_api.compat import compat_urllib_error
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_web_api import (
        __version__ as __webversion__,
        Client as WebClient,
        ClientError as WebClientError,
        ClientLoginError as WebClientLoginError,
        ClientCookieExpiredError as WebClientCookieExpiredError,
        ClientCompatPatch as WebClientCompatPatch)
    from instagram_web_api.compat import compat_urllib_error


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


class ApiTestBase(unittest.TestCase):
    """Main base class for private api tests."""

    def __init__(self, testname, api, user_id=None, media_id=None):
        super(ApiTestBase, self).__init__(testname)
        self.api = api
        self.test_user_id = user_id
        self.test_media_id = media_id
        self.sleep_interval = 2.5
        if testname.endswith('_mock'):
            self.sleep_interval = 0      # sleep a bit between tests to avoid HTTP429 errors

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        time.sleep(self.sleep_interval)


class WebApiTestBase(unittest.TestCase):
    """Main base class for web api tests."""

    def __init__(self, testname, api):
        super(WebApiTestBase, self).__init__(testname)
        self.api = api
        self.sleep_interval = 2.5
        if testname.endswith('_mock'):
            self.sleep_interval = 0   # sleep a bit between tests to avoid HTTP429 errors

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.test_user_id = '25025320'
        self.test_user_name = 'instagram'
        self.test_media_shortcode = 'BJL-gjsDyo1'
        self.test_media_shortcode2 = 'BVRqQxmj2TA'
        self.test_media_id = '1009392755603152985'
        self.test_comment_id = '1234567890'

    def tearDown(self):
        time.sleep(self.sleep_interval)


class MockResponse(object):
    """A mock class to emulate api responses."""

    def __init__(self, code=200, content_type='', body=''):
        self.code = 200
        self.content_type = content_type
        self.body = body

    def info(self):
        return {'Content-Type': self.content_type}

    def read(self):
        return self.body.encode('utf8')
