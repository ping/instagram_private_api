# -*- coding: utf-8 -*-


class ClientError(Exception):
    """Generic error class, catch-all for most client issues.
    """
    def __init__(self, msg, code=None):
        self.code = code or 0
        super(ClientError, self).__init__(msg)

    @property
    def msg(self):
        return self.args[0]


class ClientLoginError(ClientError):
    """Raised when login fails."""
    pass


class ClientCookieExpiredError(ClientError):
    """Raised when cookies have expired."""
    pass


class ClientConnectionError(ClientError):
    """Raised due to network connectivity-related issues"""
    pass
