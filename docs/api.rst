.. _api:

Developer Interface
===================

This page of the documentation will cover all methods and classes available to the developer.

The api currently has two main interfaces:

- `App API`_
    - :class:`instagram_private_api.Client`
    - :class:`instagram_private_api.ClientCompatPatch`
    - :class:`instagram_private_api.ClientError`
    - :class:`instagram_private_api.ClientLoginError`
    - :class:`instagram_private_api.ClientLoginRequiredError`
    - :class:`instagram_private_api.ClientCookieExpiredError`
    - :class:`instagram_private_api.ClientThrottledError`
    - :class:`instagram_private_api.ClientReqHeadersTooLargeError`
    - :class:`instagram_private_api.ClientConnectionError`
    - :class:`instagram_private_api.ClientCheckpointRequiredError`
    - :class:`instagram_private_api.ClientChallengeRequiredError`
    - :class:`instagram_private_api.ClientSentryBlockError`
    - :class:`instagram_private_api.MediaRatios`
    - :class:`instagram_private_api.MediaTypes`

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

.. automodule:: instagram_private_api

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
