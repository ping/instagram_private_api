# Instagram Private API

A Python wrapper for the Instagram private API with no 3rd party dependencies. Supports both the app and web APIs.

![](https://img.shields.io/badge/Python-2.7-green.svg)
![](https://img.shields.io/badge/Python-3.5-green.svg)
![License](https://img.shields.io/badge/license-MIT_License-blue.svg)
[![Release](https://img.shields.io/badge/release-v1.0.6-orange.svg)](https://github.com/ping/instagram_private_api/releases)
[![Docs](https://img.shields.io/badge/docs-readthedocs.io-ff4980.svg)](https://instagram-private-api.readthedocs.io/en/latest/)

## Overview

I wrote this to access Instagram's API when they clamped down on developer access. Because this is meant to achieve [parity](COMPAT.md) with the [official public API](https://www.instagram.com/developer/endpoints/), methods not available in the public API will generally have lower priority.

Problems? Please check the [docs](https://instagram-private-api.readthedocs.io/en/latest/) before submitting an issue.

## Documentation

Documentation is available at https://instagram-private-api.readthedocs.io/en/latest/

## Install

No 3rd-party libraries required. Just drop one of or both folders [``instagram_private_api/``](instagram_private_api/) and [``instagram_web_api/``](instagram_web_api/) into your project path or pip install with:

``pip install git+ssh://git@github.com/ping/instagram_private_api.git@1.0.6``

To update:

``pip install git+ssh://git@github.com/ping/instagram_private_api.git@1.0.6 --upgrade``

To update with latest repo code:

``pip install git+ssh://git@github.com/ping/instagram_private_api.git --upgrade --force-reinstall``

Tested on Python 2.7 and 3.5.

## Usage
The [app API client](instagram_private_api/) emulates the official app and has a larger set of functions. The [web API client](instagram_web_api/) has a smaller set but can be used without logging in.

Your choice will depend on your use case.

The [``examples/``](examples/) and [``tests/``](tests/) are a good source of detailed sample code on how to use the clients, including a simple way to save the auth cookie for reuse.

### Option 1: Use the [official app's API](instagram_private_api/)

```python

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
```


### Option 2: Use the [official website's API](instagram_web_api/)

```python

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
```

### Avoiding Re-login
You are advised to persist/cache the auth cookie details to avoid logging in every time you make an api call. Excessive logins is a surefire way to get your account flagged for removal. It's also advisable to cache the client details such as user agent, etc together with the auth details.

The saved auth cookie can be reused for up to **90 days**.

## Legal

Disclaimer: This is not affliated, endorsed or certified by Instagram. This is an independent and unofficial API. Strictly **not for spam**. Use at your own risk.
