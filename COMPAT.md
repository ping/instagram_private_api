# Support for Official Endpoints

Note: ``api.*()`` methods refer to using the [app api client](instapi/) while ``web.*()`` methods refer to the [web api client](instagram_web_api/)

Official Endpoints | Availability | Notes |
 ------- | :----------: | ----- |
[Users](https://www.instagram.com/developer/endpoints/users/) | 
/users/self | Yes | [``api.current_user()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.current_user), [``web.user_info()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.user_info) with account userid
/users/``user-id`` | Yes | [``api.user_info()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.user_info), [``web.user_info()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.user_info)
/users/self/media/recent | Yes | Use [``api.user_feed()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.user_feed), [``web.user_feed()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.user_feed) with account userid
/users/``user-id``/media/recent | Yes | [``api.user_feed()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.user_feed), [``web.user_feed()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.user_feed)
/users/self/media/liked | Yes | [``api.feed_liked()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.feed_liked)
[Relationships](https://www.instagram.com/developer/endpoints/relationships/) | 
/users/self/follows | Yes | Use [``api.user_following()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.user_following), [``web.user_following()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.user_following) with account userid
/users/self/followed-by | Yes | Use [``api.user_followers()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.user_followers), [``web.user_followers()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.user_followers) with account userid
/users/self/requested-by | Yes | [``api.friendships_pending()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.friendships_pending)
/users/``user-id``/relationship | Yes | [``api.friendships_show()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.friendships_show), [``api.friendships_create()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.friendships_create), [``api.friendships_destroy()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.friendships_destroy), [``web.friendships_create()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.friendships_create), [``web.friendships_destroy()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.friendships_destroy)
[Media](https://www.instagram.com/developer/endpoints/media/) |
/media/``media-id`` | Yes | [``api.media_info()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.media_info), [``web.media_info()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.media_info)
/media/shortcode/``shortcode`` | Yes | Use [``api.oembed()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.oembed) to get the media_id and then call [``api.media_info()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.media_info) with it
/media/search | No
[Comments](https://www.instagram.com/developer/endpoints/comments/) |
/media/``media-id``/comments | Yes | [``api.media_comments()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.media_comments), [``api.media_n_comments()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.media_n_comments), [``api.post_comment()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.post_comment), [``web.media_comments()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.media_comments), [``web.post_comment()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.post_comment)
/media/``media-id``/comments/``comment-id`` | Yes | [``api.delete_comment()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.delete_comment), [``web.delete_comment()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.delete_comment)
[Likes](https://www.instagram.com/developer/endpoints/likes/) |
/media/``media-id``/likes | Yes | [``api.media_likers()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.media_likers), [``api.post_like()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.post_like), [``api.delete_like()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.delete_like), [``web.post_like()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.post_like), [``web.delete_like()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.delete_like)
[Tags](https://www.instagram.com/developer/endpoints/tags/) |
/tags/``tag-name`` | Yes | [``api.tag_info()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.tag_info)
/tags/``tag-name``/media/recent | Yes | [``api.feed_tag()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.feed_tag)
/tags/search | Yes | [``api.tag_search()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.tag_search), [``web.search()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.search)
[Locations](https://www.instagram.com/developer/endpoints/locations/) |
/locations/``location-id`` | Yes | [``api.location_info()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.location_info)
/locations/``location-id``/media/recent | Yes | [``api.feed_location()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.feed_location)
/locations/search | Yes | [``api.location_search()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.location_search), [``web.search()``](https://instapi.readthedocs.io/en/latest/api.html#instagram_web_api.Client.search)
[Embedding](https://www.instagram.com/developer/embedding/) |
/embed | Yes | [``api.oembed()``](https://instapi.readthedocs.io/en/latest/api.html#instapi.Client.oembed)
/p/``shortcode``/media | No
