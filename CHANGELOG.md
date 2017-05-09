# Change Log

## 1.2.7 (pending)
- New endpoints: ``api.friendships_unblock()``, ``api.block_friend_reel()``, ``api.unblock_friend_reel()``, ``api.set_reel_block_status()``, ``api.blocked_reels()``, ``api.blocked_user_list()``, ``api.user_reel_settings()``,  ``api.set_reel_settings()``
- Update ``api. media_seen()``
- Minor fixes

## 1.2.6
- Change default user agent constants
- Video:
    - implement chunks upload retry
    - remove configure delay
    - support using a file-like object instead of having the whole file in memory
- Implement collections
- Update app version to 10.16.0
- Other minor fixes

## 1.2.5
- Update app version to 10.15.0
- New ad_id property for login
- Update ``friendships_create()``, ``friendships_destroy()``, ``post_comment()``, ``post_like()``, ``delete_like()``.

## 1.2.4
- Fix the case when a cookie doesn't have an expiry date

## 1.2.3
- Update app version to 10.14.0

## 1.2.2
- Bug fix ``configure_video()``

## 1.2.1
- New helper method ``user_broadcast()`` to get a user's live broadcast
- Add new filters to ``ClientCompatPatch``

## 1.2.0
- Invalid parameters now consistently raise ValueError. Affected endpoints can be found in 146a84b.
- New ClientThrottledError for 429 (too many requests) errors

## 1.1.5
- Fix pip setup
- Fix web client search
- Add size validation for post_photo and post_video

## 1.1.4
- Update story configure endpoint and parameters
- Validate video story duration
- New utility class InstagramID for ID/shortcode conversions

## 1.1.3
Minor improvements

## 1.1.2
- New check username endpoint ``check_username()``
- New comment likers endpoint ``comment_likers()``
- Better Python 3 compatibility

## 1.1.1
- Support album posting with ``post_album()``
- New stickers endpoint
- Internal refactoring

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
