.. _api:

Developer Interface
===================

This page of the documentation will cover all methods and classes available to the developer.

The api currently has two main interfaces:

- `App API`_
    - `instagram_private_api.Client`_
    - `instagram_private_api.ClientCompatPatch`_
    - `instagram_private_api.errors`_
- `Web API`_
    - `instagram_web_api.Client`_
    - `instagram_web_api.ClientCompatPatch`_
    - `instagram_web_api.errors`_


App API
-----------

.. automodule:: instagram_private_api

.. _instagram_private_api.Client:

.. autoclass:: Client
   :special-members: __init__
   :inherited-members:

.. _instagram_private_api.ClientCompatPatch:

.. autoclass:: ClientCompatPatch
   :special-members: __init__
   :inherited-members:

.. _instagram_private_api.errors:

.. autoexception:: ClientError
.. autoexception:: ClientLoginError
.. autoexception:: ClientLoginRequiredError
.. autoexception:: ClientCookieExpiredError

Web API
-------------------

.. automodule:: instagram_web_api

.. _instagram_web_api.Client:

.. autoclass:: Client
   :special-members: __init__
   :inherited-members:

.. _instagram_web_api.ClientCompatPatch:

.. autoclass:: ClientCompatPatch
   :special-members: __init__
   :inherited-members:

.. _instagram_web_api.errors:

.. autoexception:: ClientError
.. autoexception:: ClientLoginError
.. autoexception:: ClientCookieExpiredError
