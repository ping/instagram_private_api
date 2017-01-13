### Support for Official Endpoints

Note: ``api.*()`` methods refer to using the [private api client](instagram_private_api/) while ``web.*()`` methods refer to the [web api client](instagram_web_api/)

Official Endpoints | Availability | Notes |
 ------- | :----------: | ----- |
[Users] (https://www.instagram.com/developer/endpoints/users/) | 
/users/self | Yes | ``api.current_user()``, ``web.user_info()`` with account userid
/users/``user-id`` | Yes | ``api.user_info()``, ``web.user_info()``
/users/self/media/recent | Yes | Use ``api.user_feed()``, ``web.user_feed()`` with account userid
/users/``user-id``/media/recent | Yes | ``api.user_feed()``, ``web.user_feed()``
/users/self/media/liked | Yes | ``api.feed_liked()``
[Relationships] (https://www.instagram.com/developer/endpoints/relationships/) | 
/users/self/follows | Yes | Use ``api.user_following()``, ``web.user_following()`` with account userid
/users/self/followed-by | Yes | Use ``api.user_followers()``, ``web.user_followers()`` with account userid
/users/self/requested-by | Yes | ``api.friendships_pending()``
/users/``user-id``/relationship | Yes | ``api.friendships_show()``, ``api.friendships_create()``, ``api.friendships_destroy()``, ``web.friendships_create()``, ``web.friendships_destroy()``
[Media] (https://www.instagram.com/developer/endpoints/media/) |
/media/``media-id`` | Yes | ``api.media_info(), web.media_info()``
/media/shortcode/``shortcode`` | Yes | Use ``api.oembed()`` to get the media_id and then call ``api.media_info()`` with it
/media/search | No
[Comments] (https://www.instagram.com/developer/endpoints/comments/) |
/media/``media-id``/comments | Yes | ``api.media_comments()``, ``api.media_n_comments()``, ``api.post_comment()``, ``web.media_comments()``, ``web.post_comment()``
/media/``media-id``/comments/``comment-id`` | Yes | ``api.delete_comment()``, ``web.delete_comment()``
[Likes] (https://www.instagram.com/developer/endpoints/likes/) |
/media/``media-id``/likes | Yes | ``api.media_likers()``, ``api.post_like()``, ``api.delete_like()``, ``web.post_like()``, ``web.delete_like()``
[Tags] (https://www.instagram.com/developer/endpoints/tags/) |
/tags/``tag-name`` | Yes | ``api.tag_info()``
/tags/``tag-name``/media/recent | Yes | ``api.feed_tag()``
/tags/search | Yes | ``api.tag_search()``, ``web.search()``
[Locations](https://www.instagram.com/developer/endpoints/locations/) |
/locations/``location-id`` | Yes | ``api.location_info()``
/locations/``location-id``/media/recent | Yes | ``api.feed_location()``
/locations/search | Yes | ``api.location_search()``, ``web.search()``
[Embedding] (https://www.instagram.com/developer/embedding/) |
/embed | Yes | ``api.oembed()``
/p/``shortcode``/media | No
