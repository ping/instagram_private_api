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
