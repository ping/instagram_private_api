# -*- coding: utf-8 -*-
import logging
import json
import re

logger = logging.getLogger(__name__)


class ClientErrorCodes(object):
    """Holds static constant values for the http error codes returned from IG"""

    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    REQ_HEADERS_TOO_LARGE = 431


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
    """Raised when client detects an http 429 Too Many Requests response."""
    pass


class ClientReqHeadersTooLargeError(ClientError):
    """Raised when client detects an http 431 Request Header Fields Too Large response."""
    pass


class ClientConnectionError(ClientError):
    """Raised due to network connectivity-related issues"""
    pass


class ClientCheckpointRequiredError(ClientError):
    """Raise when IG detects suspicious activity from your account"""

    @property
    def challenge_url(self):
        try:
            error_info = json.loads(self.error_response)
            return error_info.get('challenge', {}).get('url') or error_info.get('checkpoint_url')
        except ValueError as ve:
            logger.warning('Error parsing error response: {}'.format(str(ve)))
        return None


class ClientChallengeRequiredError(ClientCheckpointRequiredError):
    """Raise when IG detects suspicious activity from your account"""


class ClientSentryBlockError(ClientError):
    """Raise when IG has flagged your account for spam or abusive behavior"""
    pass


class ClientFeedbackRequiredError(ClientError):
    """Raise when IG has flagged your account for spam or abusive behavior"""
    pass


class ErrorHandler(object):

    KNOWN_ERRORS_MAP = [
        {'patterns': ['bad_password', 'invalid_user'], 'error': ClientLoginError},
        {'patterns': ['login_required'], 'error': ClientLoginRequiredError},
        {
            'patterns': ['checkpoint_required', 'checkpoint_challenge_required', 'checkpoint_logged_out'],
            'error': ClientCheckpointRequiredError
        },
        {'patterns': ['challenge_required'], 'error': ClientChallengeRequiredError},
        {'patterns': ['sentry_block'], 'error': ClientSentryBlockError},
        {'patterns': ['feedback_required'], 'error': ClientFeedbackRequiredError},
    ]

    @staticmethod
    def process(http_error, error_response):
        """
        Tries to process an error meaningfully

        :param http_error: an instance of compat_urllib_error.HTTPError
        :param error_response: body of the error response
        """
        error_msg = http_error.reason
        if http_error.code == ClientErrorCodes.REQ_HEADERS_TOO_LARGE:
            raise ClientReqHeadersTooLargeError(
                error_msg,
                code=http_error.code,
                error_response=error_response)

        try:
            error_obj = json.loads(error_response)
            error_message_type = error_obj.get('error_type', '') or error_obj.get('message', '')
            if http_error.code == ClientErrorCodes.TOO_MANY_REQUESTS:
                raise ClientThrottledError(
                    error_obj.get('message'), code=http_error.code,
                    error_response=json.dumps(error_obj))

            for error_info in ErrorHandler.KNOWN_ERRORS_MAP:
                for p in error_info['patterns']:
                    if re.search(p, error_message_type):
                        raise error_info['error'](
                            error_message_type, code=http_error.code,
                            error_response=json.dumps(error_obj)
                        )
            if error_message_type:
                error_msg = '{0!s}: {1!s}'.format(http_error.reason, error_message_type)
            else:
                error_msg = http_error.reason
        except ValueError as ve:
            # do nothing else, prob can't parse json
            logger.warning('Error parsing error response: {}'.format(str(ve)))

        raise ClientError(error_msg, http_error.code, error_response)
