# -*- coding: utf-8 -*-
from .endpoints.common import MediaTypes


class ClientCompatPatch(object):
    """Utility to make entities from the private api similar to the ones
    from the public one by adding the necessary properties, and if required,
    remove any incompatible properties (to save storage space for example).
    """
    FILTERS = {
        -2: 'OES',
        -1: 'YUV',
        0: 'Normal',
        1: 'X-Pro II',
        2: 'Lo-Fi',
        3: 'Earlybird',
        10: 'Inkwell',
        14: '1977',
        15: 'Nashville',
        16: 'Kelvin',
        17: 'Mayfair',
        18: 'Sutro',
        19: 'Toaster',
        20: 'Walden',
        21: 'Hefe',
        22: 'Brannan',
        23: 'Rise',
        24: 'Amaro',
        25: 'Valencia',
        26: 'Hudson',
        27: 'Sierra',
        28: 'Willow',
        105: 'Dogpatch',
        106: 'Vesper',
        107: 'Ginza',
        108: 'Charmes',
        109: 'Stinson',
        111: 'Moon',
        112: 'Clarendon',
        113: 'Skyline',
        114: 'Gingham',
        115: 'Brooklyn',
        116: 'Ashby',
        117: 'Helena',
        118: 'Maven',
        603: 'Ludwig',
        605: 'Slumber',
        608: 'Perpetua',
        612: 'Aden',
        613: 'Juno',
        614: 'Reyes',
        615: 'Lark',
        616: 'Crema',
        640: 'BrightContrast',
        642: 'CrazyColor',
        643: 'SubtleColor',
    }

    @staticmethod
    def _get_closest_size(medias, width, height=0):
        """
        Try to extract a image/video object that will most match the resolution returned by the public API

        :param medias: list of images/videos
        :param width: desired width
        :param height: desired height
        :return:
        """
        current = None
        for media in medias:
            if not current:
                current = media
            if (abs(media['width'] - width) < abs(current['width'] - width) or
                    (media['width'] == current['width'] and not height and
                     not media['height'] == current['width']) or
                    (media['width'] == current['width'] and height and
                     abs(media['height'] - height) < abs(current['height'] - height))):
                current = media

        return current

    @staticmethod
    def _drop_keys(obj, keys):
        """
        Drop unwanted dict keys

        :param obj:
        :param keys:
        :return:
        """
        for k in keys:
            obj.pop(k, None)

    @classmethod
    def comment(cls, comment, drop_incompat_keys=False):
        """Patch a comment object"""
        comment['created_time'] = str(int(comment.get('created_at')))
        from_user = {
            'username': comment['user']['username'],
            'profile_picture': comment['user']['profile_pic_url'],
            'id': str(comment['user']['pk']),
            'full_name': comment['user']['full_name'],
        }
        comment['from'] = from_user
        comment['id'] = str(comment['pk'])
        if drop_incompat_keys:
            cls._drop_keys(
                comment,
                [
                    'bit_flags',
                    'content_type',
                    'created_at',
                    'created_at_utc',
                    'media_id',
                    'pk',
                    'status',
                    'type',
                    'user',
                    'user_id',
                ]
            )
        return comment

    @classmethod
    def media(cls, media, drop_incompat_keys=False):
        """Patch a media object"""
        media['link'] = 'https://www.instagram.com/p/{0!s}/'.format(media['code'])
        media['created_time'] = str(int(media.get('taken_at') or media.get('device_timestamp')))

        if media['media_type'] == MediaTypes.PHOTO:
            media['type'] = 'image'
        elif media['media_type'] == MediaTypes.VIDEO:
            media['type'] = 'video'
        elif media['media_type'] == MediaTypes.CAROUSEL:
            media['type'] = 'carousel'  # will be patched over below

        if media['caption']:
            media['caption']['id'] = str(media['caption']['pk'])
            media['caption']['created_time'] = str(int(media['caption']['created_at']))
            caption_from = {
                'username': media['caption']['user']['username'],
                'profile_picture': media['caption']['user']['profile_pic_url'],
                'id': str(media['caption']['user']['pk']),
                'full_name': media['caption']['user']['full_name'],
            }
            media['caption']['from'] = caption_from
            if drop_incompat_keys:
                cls._drop_keys(
                    media['caption'],
                    [
                        'bit_flags',
                        'content_type',
                        'created_at',
                        'created_at_utc',
                        'has_translation',
                        'media_id',
                        'pk',
                        'status',
                        'type',
                        'user',
                    ]
                )
        media['user'] = cls.list_user(media['user'], drop_incompat_keys=drop_incompat_keys)
        if media['media_type'] == MediaTypes.CAROUSEL and media.get('carousel_media', []):
            # patch carousel media
            for carousel_media in media.get('carousel_media', []):
                if carousel_media['media_type'] == MediaTypes.PHOTO:
                    carousel_media['type'] = 'image'
                elif carousel_media['media_type'] == MediaTypes.VIDEO:
                    carousel_media['type'] = 'video'
                image_versions2 = carousel_media.get('image_versions2', {}).get('candidates', [])
                images = {
                    'low_resolution': cls._get_closest_size(image_versions2, 320),
                    'thumbnail': cls._get_closest_size(image_versions2, 150, 150),
                    'standard_resolution': cls._get_closest_size(
                        image_versions2, carousel_media.get('original_width', 1000)),
                }
                carousel_media['images'] = images
                if carousel_media['media_type'] == MediaTypes.VIDEO:
                    video_versions = carousel_media.get('video_versions', [])
                    videos = {
                        'low_bandwidth': cls._get_closest_size(video_versions, 480),
                        'standard_resolution': cls._get_closest_size(
                            video_versions, carousel_media.get('original_width', 640)),
                        'low_resolution': cls._get_closest_size(video_versions, 640),
                    }
                    if drop_incompat_keys:
                        [cls._drop_keys(i, ['type']) for i in list(videos.values())]
                    carousel_media['videos'] = videos

                # patch user tags
                if carousel_media.get('usertags', {}).get('in', []):
                    usertags = carousel_media['usertags']['in']
                    user_tags = []
                    for ut in usertags:
                        pos = {'y': ut['position'][1], 'x': ut['position'][0]}
                        user = ut['user']
                        user['id'] = str(ut['user']['pk'])
                        user['profile_picture'] = ut['user']['profile_pic_url']
                        if drop_incompat_keys:
                            cls._drop_keys(user, ['profile_pic_url', 'pk', 'is_private'])

                        user_tags.append({
                            'position': pos,
                            'user': user,
                        })
                    carousel_media['users_in_photo'] = user_tags
                # patch location
                if 'location' not in carousel_media or not carousel_media['location'].get('lat'):
                    carousel_media['location'] = None
                else:
                    carousel_media['location']['latitude'] = carousel_media['location']['lat']
                    carousel_media['location']['longitude'] = carousel_media['location']['lng']
                    carousel_media['location']['id'] = carousel_media['location']['pk']

            first_carousel_media = media['carousel_media'][0]
            media['images'] = first_carousel_media['images']
            media['type'] = first_carousel_media['type']
            if first_carousel_media['media_type'] == MediaTypes.VIDEO:
                media['videos'] = first_carousel_media['videos']
        else:
            image_versions2 = media.get('image_versions2', {}).get('candidates', [])
            images = {
                'low_resolution': cls._get_closest_size(image_versions2, 320),
                'thumbnail': cls._get_closest_size(image_versions2, 150, 150),
                'standard_resolution': cls._get_closest_size(image_versions2, media.get('original_width', 1000)),
            }
            media['images'] = images

        if media['media_type'] == MediaTypes.VIDEO:
            video_versions = media.get('video_versions', [])
            videos = {
                'low_bandwidth': cls._get_closest_size(video_versions, 480),
                'standard_resolution': cls._get_closest_size(video_versions, media.get('original_width', 640)),
                'low_resolution': cls._get_closest_size(video_versions, 640),
            }
            if drop_incompat_keys:
                [cls._drop_keys(i, ['type']) for i in list(videos.values())]
            media['videos'] = videos

        likes = {
            'count': media.get('like_count', 0),
            'data': []
        }
        media['likes'] = likes
        comments = {
            'count': media.get('comment_count', 0),
            # Patch comment too
            'data': [
                cls.comment(c, drop_incompat_keys=drop_incompat_keys)
                for c in media.get('comments', [])
            ]
        }
        media['comments'] = comments
        if media.get('preview_comments'):
            [
                cls.comment(c, drop_incompat_keys=drop_incompat_keys)
                for c in media.get('preview_comments', [])
            ]

        media['attribution'] = None
        if media.get('filter_type') is not None and media.get('filter_type') in cls.FILTERS:
            media['filter'] = cls.FILTERS[media.get('filter_type')]
        else:
            media['filter'] = ''
        media['user_has_liked'] = media.get('has_liked', False)

        # Try to preserve location even if there's no lat/lng/pk
        if 'location' not in media or not media['location']:
            media['location'] = None
        elif (media.get('location', {}).get('lat')
              and media.get('location', {}).get('lng')
              and media.get('location', {}).get('pk')):
            media['location']['latitude'] = media['location']['lat']
            media['location']['longitude'] = media['location']['lng']
            media['location']['id'] = media['location']['pk']
        # For stories
        if (not media.get('location')
                and media.get('story_locations')
                and media.get('story_locations', [{}])[0].get('location')):
            story_location = media['story_locations'][0]['location']
            if (story_location.get('lat')
                    and story_location.get('lng')
                    and story_location.get('pk')):
                media['location'] = story_location

        media['tags'] = []
        if media.get('usertags', {}).get('in', []):
            usertags = media['usertags']['in']
            user_tags = []
            for ut in usertags:
                pos = {'y': ut['position'][1], 'x': ut['position'][0]}
                user = ut['user']
                user['id'] = str(ut['user']['pk'])
                user['profile_picture'] = ut['user']['profile_pic_url']
                if drop_incompat_keys:
                    cls._drop_keys(user, ['profile_pic_url', 'pk', 'is_private'])

                user_tags.append({
                    'position': pos,
                    'user': user,
                })
            media['users_in_photo'] = user_tags
        elif media.get('reel_mentions'):
            reel_mentions = media['reel_mentions']
            user_tags = []
            for rm in reel_mentions:
                pos = {'y': rm['y'], 'x': rm['x']}
                user = rm['user']
                user['id'] = str(rm['user']['pk'])
                user['profile_picture'] = rm['user']['profile_pic_url']
                if drop_incompat_keys:
                    cls._drop_keys(user, ['profile_pic_id', 'profile_pic_url', 'pk', 'is_private'])
                user_tags.append({
                    'position': pos,
                    'user': user,
                })
            media['users_in_photo'] = user_tags
        else:
            media['users_in_photo'] = []

        if drop_incompat_keys:
            cls._drop_keys(
                media,
                [
                    'can_viewer_save',
                    'caption_is_edited',
                    'client_cache_key',
                    'code',
                    'comment_count',
                    'comments_disabled',
                    'comment_likes_enabled',
                    'device_timestamp',
                    'filter_type',
                    'has_audio',
                    'has_liked',
                    'has_more_comments',
                    'image_versions2',
                    'is_reel_media',
                    'lat',
                    'like_count',
                    'lng',
                    'max_num_visible_preview_comments',
                    'media_type',
                    'next_max_id',
                    'organic_tracking_token',
                    'original_height',
                    'original_width',
                    'photo_of_you',
                    'pk',
                    'preview_comments',
                    'reel_mentions',
                    'saved_collection_ids',
                    'taken_at',
                    'top_likers',
                    'video_duration',
                    'video_versions',
                    'view_count',
                    'visibility',
                ]
            )
            if media['location']:
                cls._drop_keys(
                    media['location'],
                    [
                        'address',
                        'city',
                        'external_id',
                        'external_source',
                        'facebook_places_id',
                        'foursquare_v2_id',
                        'lat',
                        'lng',
                        'pk',
                        'state',
                    ]
                )
        return media

    @classmethod
    def user(cls, user, drop_incompat_keys=False):
        """Patch a user object """
        user['id'] = str(user['pk'])
        user['bio'] = user.get('biography', '')
        user['profile_picture'] = user['profile_pic_url']
        user['website'] = user.get('external_url', '')
        if 'media_count' in user and 'follower_count' in user and 'following_count' in user:
            counts = {
                'media': user['media_count'],
                'followed_by': user['follower_count'],
                'follows': user['following_count']
            }
            user['counts'] = counts
        if drop_incompat_keys:
            cls._drop_keys(
                user,
                [
                    'auto_expand_chaining',
                    'biography',
                    'external_lynx_url',
                    'external_url',
                    'follower_count',
                    'following_count',
                    'geo_media_count',
                    'has_anonymous_profile_picture',
                    'has_chaining',
                    'hd_profile_pic_url_info',
                    'hd_profile_pic_versions',
                    'include_direct_blacklist_status',
                    'is_business',
                    'is_favorite',
                    'is_private',
                    'is_unpublished',
                    'is_verified',
                    'media_count',
                    'pk',
                    'profile_context',
                    'profile_pic_id',
                    'profile_pic_url',
                    'usertags_count',
                ]
            )
        return user

    @classmethod
    def list_user(cls, user, drop_incompat_keys=False):
        """
        Patch a list user object, example in
        :meth:`Client.user_following`, :meth:`Client.user_followers`, :meth:`Client.search_users`
        """
        user['id'] = str(user['pk'])
        user['profile_picture'] = user['profile_pic_url']
        if drop_incompat_keys:
            cls._drop_keys(
                user,
                [
                    'byline',
                    'follower_count',
                    'friendship_status',
                    'has_anonymous_profile_picture',
                    'has_chaining',
                    'is_favorite',
                    'is_private',
                    'is_unpublished',
                    'is_verified',
                    'mutual_followers_count',
                    'pk',
                    'profile_pic_url',
                    'social_context',
                    'unseen_count',
                ]
            )
        return user
