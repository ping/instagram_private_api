.. _usage:

Installation
============

Pip
---

Install via pip

.. code-block:: bash

    $ pip install instapi

Update your install with the latest release

.. code-block:: bash

    $ pip install instapi --upgrade

Force an update from source

.. code-block:: bash

    $ pip install instapi --upgrade --force-reinstall


Source Code
-----------

The library is maintained on GitHub. Feel free to clone the repository.

.. code-block:: bash

    git clone git://github.com/breuerfelix/instapi.git


Usage
=====

The private app API client emulates the official app and has a larger number of functions. 

App API
-----------

.. code-block:: python

    from instapi import Client, ClientCompatPatch

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

Avoiding Re-login
-----------------

You are advised to persist/cache the auth cookie details to avoid logging in every time you make an api call. Excessive logins is a surefire way to get your account flagged for removal. It's also advisable to cache the client details such as user agent, etc together with the auth details.

The saved auth cookie can be reused for up to 90 days.

An example of how to save and reuse the auth setting can be found in the examples_.

.. _examples: https://github.com/breuerfelix/instapi/blob/master/examples/savesettings_logincallback.py
