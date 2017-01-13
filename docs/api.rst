.. _api:

Developer Interface
===================

.. module:: instagram_private_api

This page of the documentation will cover all methods and classes available to the developer.

The api currently has two main interfaces:

- `Private API`_
    - `instagram_private_api.Client`_
    - `instagram_private_api.ClientCompatPatch`_
    - `instagram_private_api.errors`_
- `Web API`_
    - `instagram_web_api.Client`_
    - `instagram_web_api.ClientCompatPatch`_
    - `instagram_web_api.errors`_


Private API
-----------

.. _instagram_private_api.Client:

.. autoclass:: instagram_private_api.Client
   :special-members: __init__
   :inherited-members:

.. _instagram_private_api.ClientCompatPatch:

.. autoclass:: instagram_private_api.ClientCompatPatch
   :special-members: __init__
   :inherited-members:

.. _instagram_private_api.errors:

.. autoexception:: instagram_private_api.ClientError
.. autoexception:: instagram_private_api.ClientLoginError
.. autoexception:: instagram_private_api.ClientLoginRequiredError
.. autoexception:: instagram_private_api.ClientCookieExpiredError

Web API
-------------------

.. _instagram_web_api.Client:

.. autoclass:: instagram_web_api.Client
   :special-members: __init__
   :inherited-members:

.. _instagram_web_api.ClientCompatPatch:

.. autoclass:: instagram_web_api.ClientCompatPatch
   :special-members: __init__
   :inherited-members:

.. _instagram_web_api.errors:

.. autoexception:: instagram_web_api.ClientError
.. autoexception:: instagram_web_api.ClientLoginError
.. autoexception:: instagram_web_api.ClientCookieExpiredError
