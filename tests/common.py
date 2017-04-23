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
        ClientCookieExpiredError, ClientCompatPatch,
        ClientLoginRequiredError)
    from instagram_private_api.utils import (
        InstagramID, gen_user_breadcrumb,
        max_chunk_size_generator, max_chunk_count_generator
    )   # noqa
    from instagram_private_api.constants import Constants
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        __version__, Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientCompatPatch,
        ClientLoginRequiredError)
    from instagram_private_api.utils import (
        InstagramID, gen_user_breadcrumb,
        max_chunk_size_generator, max_chunk_count_generator
    )   # noqa
    from instagram_private_api.constants import Constants

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
    if '__class__' in json_object:
        if json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


class ApiTestBase(unittest.TestCase):

    def __init__(self, testname, api, user_id=None, media_id=None):
        super(ApiTestBase, self).__init__(testname)
        self.api = api
        self.test_user_id = user_id
        self.test_media_id = media_id

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        if not self._testMethodName.endswith('_mock'):
            time.sleep(2.5)   # sleep a bit between tests to avoid HTTP429 errors


class WebApiTestBase(unittest.TestCase):

    def __init__(self, testname, api):
        super(WebApiTestBase, self).__init__(testname)
        self.api = api

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.test_user_id = '25025320'
        self.test_media_shortcode = 'BJL-gjsDyo1'
        self.test_media_id = '1009392755603152985'
        self.test_comment_id = '1234567890'

    def tearDown(self):
        if not self._testMethodName.endswith('_mock'):
            time.sleep(2.5)   # sleep a bit between tests to avoid HTTP429 errors
