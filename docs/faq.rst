.. _faq:

FAQ
===

.. contents::
   :local:
   :backlinks: top

Can I create accounts with this library?
----------------------------------------
No. This library will not support account creation because of abuse by spammers. If you need an account, use the official app or website.

Can I _____ with this library?
---------------------------------

This library is limited to what the mobile app/web interface can do. If you can't do it on those platforms, you can't do it through the library.

What does error code XXX mean?
------------------------------

- **400**: Bad request. Please check the parameters specified.
- **403**: The method requires authentication (web client) or the request has been denied by IG.
- **404**: The entity requested is not found (web client) or the endpoint does not exist.
- **429**: Too many requests. You're making too many calls.

IG may also return other 4XX or 5XX codes.

"Your version of Instagram is out of date. Please upgrade your app to log in to Instagram."
-------------------------------------------------------------------------------------------

Instagram is rejecting the app version that the lib is using. 

If discarding the cached auth and relogging in does not work, you may need to:

#. update the lib, or 
#. extract the latest signature key and version from the latest `Instagram APK`_ or from https://github.com/mgp25/Instagram-API/blob/master/src/Constants.php.

.. _Instagram APK: http://www.apkmirror.com/apk/instagram/instagram-instagram

With the new sig key and app version, you can modify the client like so

.. code-block:: python

    new_app_version = '10.3.2'
    new_sig_key = '5ad7d6f013666cc93c88fc8af940348bd067b68f0dce3c85122a923f4f74b251'
    new_key_ver = '4'           # does not freq change
    new_ig_capa = '3ToAAA=='    # does not freq change

    api = Client(
        user_name, password,
        app_version=new_app_version,
        signature_key=new_sig_key,
        key_version= new_key_ver,
        ig_capabilities=new_ig_capa)

How to direct message/share?
----------------------------
There are no plans to implement direct messaging/sharing functions.

What does ``sentry_block`` error mean?
--------------------------------------
This is the response for detected spam/bot behavior. Stop using the api in whatever way that triggered this reponse.

Why are the captions not posted?
--------------------------------
This is due to your account / access location (IP) being soft-blocked.

What does ``checkpoint_challenge_required``, ``challenge_required`` mean?
-------------------------------------------------------------------------
Your access attempt has been flagged. Login manually to pass the required challenge.
