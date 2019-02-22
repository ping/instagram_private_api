.. _usage:

Installation
============

Pip
---

Install via pip

.. code-block:: bash

    $ pip install git+https://git@github.com/ping/instagram_private_api.git@1.6.0

Update your install with the latest release

.. code-block:: bash

    $ pip install git+https://git@github.com/ping/instagram_private_api.git@1.6.0 --upgrade

Force an update from source

.. code-block:: bash

    $ pip install git+https://git@github.com/ping/instagram_private_api.git --upgrade --force-reinstall


Source Code
-----------

The library is maintained on GitHub. Feel free to clone the repository.

.. code-block:: bash

    git clone git://github.com/ping/instagram_private_api.git


Usage
=====

The private app API client emulates the official app and has a larger number of functions. 
The web API client has a smaller set but can be used without logging in.

Your choice will depend on your use case.

App API
-----------

.. code-block:: python

    from instagram_private_api import Client, ClientCompatPatch

    user_name = 'YOUR_LOGIN_USER_NAME'
    password = 'YOUR_PASSWORD'

    api = Client(user_name, password)
    results = api.feed_timeline()
    items = results.get('items', [])
    for item in items:
        # Manually patch the entity to match the public api as closely as possible, optional
        # To automatically patch entities, initialise the Client with auto_patch=True
        ClientCompatPatch.media(item)
        print(media['code'])


Web API
-------

.. code-block:: python

    from instagram_web_api import Client, ClientCompatPatch, ClientError, ClientLoginError

    # Without any authentication
    web_api = Client(auto_patch=True, drop_incompat_keys=False)
    user_feed_info = web_api.user_feed('329452045', count=10)
    for post in user_feed_info:
        print('%s from %s' % (post['link'], post['user']['username']))

    # Some endpoints, e.g. user_following are available only after authentication
    authed_web_api = Client(
        auto_patch=True, authenticate=True,
        username='YOUR_USERNAME', password='YOUR_PASSWORD')

    following = authed_web_api.user_following('123456')
    for user in following:
        print(user['username'])

    # Note: You can and should cache the cookie even for non-authenticated sessions.
    # This saves the overhead of a single http request when the Client is initialised.  


Avoiding Re-login
-----------------

You are advised to persist/cache the auth cookie details to avoid logging in every time you make an api call. Excessive logins is a surefire way to get your account flagged for removal. It's also advisable to cache the client details such as user agent, etc together with the auth details.

The saved auth cookie can be reused for up to 90 days.

An example of how to save and reuse the auth setting can be found in the examples_.

.. _examples: https://github.com/ping/instagram_private_api/blob/master/examples/savesettings_logincallback.py
