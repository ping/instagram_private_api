# -*- coding: utf-8 -*-


class ClientErrorCodes(object):
    """Holds static constant values for the http error codes returned from IG"""

    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429


class ClientError(Exception):
    """Generic error class, catch-all for most client issues.
    """
    def __init__(self, msg, code=None, error_response=''):
        self.code = code or 0
        self.error_response = error_response
        super(ClientError, self).__init__(msg)

    @property
    def msg(self):
        return self.args[0]


class ClientLoginError(ClientError):
    """Raised when login fails."""
    pass


class ClientLoginRequiredError(ClientError):
    """Raised when login is required."""
    pass


class ClientCookieExpiredError(ClientError):
    """Raised when cookies have expired."""
    pass


class ClientThrottledError(ClientError):
    """Raised when client detects a 429 http response."""
    pass
