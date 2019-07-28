from .client import Client
from .compatpatch import ClientCompatPatch
from .errors import (
    ClientError, ClientLoginError, ClientLoginRequiredError,
    ClientCookieExpiredError, ClientThrottledError, ClientConnectionError,
    ClientCheckpointRequiredError, ClientChallengeRequiredError,
    ClientSentryBlockError, ClientReqHeadersTooLargeError,
)
from .endpoints.upload import MediaRatios
from .endpoints.common import MediaTypes

from os import path

here = path.abspath(path.dirname(__file__))

def readall(*args):
    with open(path.join(here, *args), encoding='utf-8') as fp:
        return fp.read()

version = readall('version.txt')

__version__ = version
