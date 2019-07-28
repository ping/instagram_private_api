.. _api:

Developer Interface
===================

This page of the documentation will cover all methods and classes available to the developer.

The api currently has two main interfaces:

- `App API`_
    - :class:`instapi.Client`
    - :class:`instapi.ClientCompatPatch`
    - :class:`instapi.ClientError`
    - :class:`instapi.ClientLoginError`
    - :class:`instapi.ClientLoginRequiredError`
    - :class:`instapi.ClientCookieExpiredError`
    - :class:`instapi.ClientThrottledError`
    - :class:`instapi.ClientReqHeadersTooLargeError`
    - :class:`instapi.ClientConnectionError`
    - :class:`instapi.ClientCheckpointRequiredError`
    - :class:`instapi.ClientChallengeRequiredError`
    - :class:`instapi.ClientSentryBlockError`
    - :class:`instapi.MediaRatios`
    - :class:`instapi.MediaTypes`

- `Web API`_
    - :class:`instagram_web_api.Client`
    - :class:`instagram_web_api.ClientCompatPatch`
    - :class:`instagram_web_api.ClientError`
    - :class:`instagram_web_api.ClientCookieExpiredError`
    - :class:`instagram_web_api.ClientConnectionError`
    - :class:`instagram_web_api.ClientBadRequestError`
    - :class:`instagram_web_api.ClientForbiddenError`
    - :class:`instagram_web_api.ClientThrottledError`


App API
-----------

.. automodule:: instapi

.. autoclass:: Client
   :special-members: __init__
   :inherited-members:

.. autoclass:: ClientCompatPatch
   :special-members: __init__
   :inherited-members:

.. autoexception:: ClientError
.. autoexception:: ClientLoginError
.. autoexception:: ClientLoginRequiredError
.. autoexception:: ClientCookieExpiredError

.. autoclass:: MediaRatios
   :members:

.. autoclass:: MediaTypes
   :members:

Web API
-------------------

.. automodule:: instagram_web_api

.. autoclass:: Client
   :special-members: __init__
   :inherited-members:

.. autoclass:: ClientCompatPatch
   :special-members: __init__
   :inherited-members:

.. autoexception:: ClientError
.. autoexception:: ClientLoginError
.. autoexception:: ClientCookieExpiredError
