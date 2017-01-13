# -*- coding: utf-8 -*-


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
