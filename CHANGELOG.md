# Change Log

## 1.1.0
- New endpoints for app client
    * ``suggested_broadcasts()``
    * ``media_likers_chrono()``
- New method for web client: ``media_info2()`` that retrieves carousel media info
- Fixes for app api:
    * ``feed_timeline()``
    * ``broadcast_like_count()``
    * pagination fixes for ``feed_location()``, ``username_feed()``, ``saved_feed()``, ``location_related()``, ``tag_related()``, ``media_likers()``, ``feed_popular()``
    * compat patch: ``media()``
- Update app client version to 10.9.0

## 1.0.9
- New endpoints for app client
    * ``top_search()``
- Fix param validation for ``broadcast_comments()``

## 1.0.8
- New live/broadcast endpoint functions for app client
    * ``top_live_status()``
    * ``broadcast_like()``
    * ``broadcast_like_count()``
    * ``broadcast_comments()``
    * ``broadcast_heartbeat_and_viewercount()``
    * ``broadcast_comment()``

## 1.0.7
- New shortcut functions for app client
    * ``self_feed()``
    * ``post_photo_story()``
    * ``post_video_story()``
- Add more validation to ``post_video()``

## 1.0.6
- Support specification of location to ``post_photo()``, ``post_video()``
- Proxy support (alpha)
- Support usertags in ``edit_media()`` (app client)
- New endpoint functions for app client
    * ``expose()``
    * ``megaphone_log()``
    * ``discover_channels_home()``
    * ``discover_chaining()``
    * ``user_map()``
    * ``feed_popular()``
    * ``friendships_block()``
    * ``usertag_self_remove()``
    * ``edit_profile()``
    * ``logout()``

## 1.0.5
- New disable/enable media comments endpoints
- New FB location search endpoint

## 1.0.4
- Add new settings property to help extract settings for saving

## 1.0.3
- Fix Python 3 compatibility

## 1.0.2
- Detect if authenticated cookie has expired and raise ClientCookieExpiredError

## 1.0.1
- Detect if re-login is required and raise ClientLoginRequiredError

## 1.0.0

First release

- access both the private Instagram app or web API
- CompatPatch patches the objects returned in the private API to match those returned in the public API
- can be used to largely replace the public Instagram API that is now severely restricted
