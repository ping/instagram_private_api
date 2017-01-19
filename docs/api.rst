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

- `Web API`_
    - :class:`instagram_web_api.Client`
    - :class:`instagram_web_api.ClientCompatPatch`
    - :class:`instagram_web_api.ClientError`
    - :class:`instagram_web_api.ClientCookieExpiredError`


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
