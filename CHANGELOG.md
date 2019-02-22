# Change Log

## 1.6.0
- Web API:
    * Add ``highlight_reels()`` and ``highlight_reel_media()``
    * Add ``tagged_user_feed()``
    * Add ``tag_story_feed()`` and ``location_story_feed()``
    * Update query hashes
    * Fix for case sensitivity for tag feed
    * Add ``delete_media()``
    * Add ``proxy_handler`` kwarg to support custom proxy handler such as socks
- App API:
    * :fire: __BREAKING CHANGE__: Change in user agent format for the app version
    * :fire: __BREAKING CHANGE__: Change in argument list for ``search_users()``
    * Add IGTV endpoints
    * Update ``media_n_comments()``, ``search_users()``, ``news()``
    * ``feed_location()`` deprecated
    * Add ``kwargs`` to ``news()`` for paging support
    * Add ``tag_section()`` and ``location_section()`` endpoints
    * Add ``proxy_handler`` kwarg to support custom proxy handler such as socks

## 1.5.7
- Web API:
    * Improve cookie expiry detection
- App API:
    * Make change to cookiejar (in 1.5.6) backward compatible

## 1.5.6
- Web API:
    * Add ``media_likers()``
    * Fix ``user_info2()``
    * Fix csrf token extraction
- App API:
    * Fix client authentication expiry
    * Improve get cookie value

## 1.5.5
- Web API:
    * Fix for changes in the ``X-Instagram-GIS`` signed header requirement

## 1.5.4
- Web API:
    * Fix for changes in the ``X-Instagram-GIS`` signed header requirement

## 1.5.3
- Web API:
    * ``client.settings`` now includes ``user_agent`` which you should persist since ``rhx_gis`` is dependent on both the ``csrftoken`` (in cookie) and the client's ``user_agent``

## 1.5.2
- Web API:
    * Fix for new ``query_hash`` param and ``X-Instagram-GIS`` signed header requirement
    * You should now store the ``rhx_gis`` value returned by ``client.settings`` along with the cookie string

## 1.5.1
- Web API:
    * Fix 403 Forbidden error when making unauthenticated requests

## 1.5.0
- App API:
    * __BREAKING CHANGE__: New arguments are needed for ``feed_tag()``, ``tag_search()``, ``user_following()``, ``user_followers()``, ``search_users()``, ``location_fb_search()``
    * New ``ClientReqHeadersTooLargeError`` error
- Web API:
    * Fix ``user_info2()``

## 1.4.1
- App API:
    * Refactored error detection. New ``ClientCheckpointRequiredError``, ``ClientChallengeRequiredError``, ``ClientSentryBlockError``
    * New highlight endpoints
    * New ``comment_inline_replies()`` endpoint
    * New ``story_viewers()`` endpoint
    * Updates for user feed and comments endpoints

## 1.4.0
- Common:
    * __BREAKING CHANGE__: New ClientConnectionError for network-related errors
- App API:
    * Add comment replies endpoint
    * Add presence endpoints
    * Add tag following endpoints
    * Update user and tag search endpoints
    * Update app version to 26
- Web API:
    * __BREAKING CHANGE__: Tag and Location feeds updated to use graphql endpoints.
    * Add timeline feed, reels tray, reels (stories) feed

## 1.3.6
- App API:
    * Minor fixes

## 1.3.5
- App API:
    * Fix video upload retry logic
    * Fix compatpatch typo
    * Improve app compatpatch for media location

## 1.3.4
- App API:
    * New endpoints: ``ignore_user()``, ``remove_follower()``, ``replay_broadcast_comments()``, ``replay_broadcast_likes()``
- Minor fixes

## 1.3.3
- Web API:
    * New endpoints: ``user_info2()``
    * Deprecate all remaining endpoints using ``query/``: ``user_info()``, ``media_info()``

## 1.3.2
- App API:
    * New endpoints: ``feed_only_me()``, ``media_only_me()``, ``media_undo_only_me()``, ``enable_post_notifications()``, ``disable_post_notifications()``
    * Deprecated: ``user_map()``, ``expose()``
    * Removed device info, keys, etc from ``settings`` property.
- Web API:
    * New endpoints: ``post_photo()``, ``tag_feed()``, ``location_feed()``
    * Removed user-agent from ``settings`` property.

## 1.3.1
- App API:
    * ``Client.standard_ratios()`` and ``Client.reel_ratios()`` is deprecated and replaced with ``MediaRatios.standard`` and ``MediaRatios.reel`` respectively.
    * Deprecated and experimental endpoints now warned with ``ClientDeprecationWarning`` and ``ClientExperimentalWarning``.
    * ``collection_feed()``, ``feed_liked()``, ``self_feed()`` have been updated to support pagination through the ``max_id`` kwarg.

## 1.3.0
This update is recommended especially for those using the web api.

- Web API:
    * __Important__: The new graphql endpoint appears to be replacing the old query endpoint. The graphql endpoint is comparatively more limited and some attributes may no longer be available.
    * You should exercise caution when using functions relying on the old query endpoints such as ``user_info()`` and ``media_info()``since IG no longer uses them.
    * ``user_feed()`` is now using the graphql endpoint and has compatibility-breaking changes.
- App API:
    * Fix regression with photo posting and profile image update.
    * __Breaking Change__: Removed ``is_video`` argument from ``reel_compatible_aspect_ratio()``

## 1.2.8
- New app client endpoint: ``api.bulk_delete_comments()``
- Prevent uploading of very small chunks when posting video
- Web API updates to use new graphql endpoints

## 1.2.7
- New endpoints: ``api.friendships_unblock()``, ``api.block_friend_reel()``, ``api.unblock_friend_reel()``, ``api.set_reel_block_status()``, ``api.blocked_reels()``, ``api.blocked_user_list()``, ``api.user_reel_settings()``,  ``api.set_reel_settings()``
- Update ``api. media_seen()``
- Fix ``ClientCompatPatch.media()`` for carousel/album posts
- Other minor fixes

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
