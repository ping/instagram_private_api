# -*- coding: utf-8 -*-
import re


class ClientCompatPatch():

    IG_IMAGE_URL_EXPR = r'/((?P<crop>[a-z])[0-9]{3}x[0-9]{3}/)'

    @classmethod
    def _generate_image_url(cls, url, size, crop):
        mobj = re.search(cls.IG_IMAGE_URL_EXPR, url)
        if not mobj:
            replacement_expr = '\g<eparam>%(crop)s%(size)sx%(size)s/' % {'crop': crop, 'size': size}
            return re.sub(r'(?P<eparam>/e[0-9]+/)', replacement_expr, url)
        replacement_expr = '/%(crop)s%(size)sx%(size)s/' % {'crop': mobj.group('crop') or crop, 'size': size}
        return re.sub(cls.IG_IMAGE_URL_EXPR, replacement_expr, url)

    @classmethod
    def _drop_keys(cls, obj, keys):
        if not obj:
            return obj
        for k in keys:
            obj.pop(k, None)

    @classmethod
    def media(cls, media, drop_incompat_keys=False):
        media['link'] = 'https://www.instagram.com/p/%s/' % media['code']
        caption = media.get('caption')
        if not caption:
            media['caption'] = None
        else:
            media['caption'] = {
                'text': caption,
                'from': media['owner'],
                'id': str(abs(hash(caption + media['code'])) % (10 ** 12)),       # generate a psuedo 12-char ID
            }
        media['tags'] = []
        media['filter'] = ''
        media['attribution'] = None
        media['user_has_liked'] = False
        media['user'] = {
            'id': media['owner']['id'],
            'username': media['owner']['username'],
            'full_name': media['owner']['full_name'],
            'profile_picture': media['owner']['profile_pic_url'],
        }
        media['type'] = 'video' if media['is_video'] else 'image'
        images = {
            'standard_resolution': {
                'url': media['display_src'],
                'width': media['dimensions']['width'],
                'height': media['dimensions']['height']},
            'low_resolution': {'url': cls._generate_image_url(media['display_src'], '320', 'p')},
            'thumbnail': {'url': cls._generate_image_url(media['display_src'], '150', 's')},
        }
        media['images'] = images
        if media['is_video']:
            videos = {
                'standard_resolution': {
                    'url': media['video_url'],
                    'width': media['dimensions']['width'],
                    'height': media['dimensions']['height']},
                'low_resolution': {'url': media['video_url']},
                'low_bandwidth': {'url': media['video_url']},
            }
            media['videos'] = videos
        media['likes'] = {
            'count': media.get('likes', {}).get('count', 0),
            'data': []
        }
        media['comments'] = {
            'count': media.get('comments', {}).get('count', 0),
            'data': []
        }
        if 'location' not in media or not media['location'] or not media['location'].get('lat'):
            media['location'] = None
        else:
            media['location']['latitude'] = media['location']['lat']
            media['location']['longitude'] = media['location']['lng']
        media['id'] = '%s_%s' % (media['id'], media['owner']['id'])
        media['created_time'] = str(media['date'])

        usertags = media.get('usertags', {}).get('nodes', [])
        if not usertags:
            media['users_in_photo'] = []
        else:
            users_in_photo = [{
                'position': {'y': ut['y'], 'x': ut['x']},
                'user': ut['user']
            } for ut in usertags]
            media['users_in_photo'] = users_in_photo

        if drop_incompat_keys:
            cls._drop_keys(
                media, [
                    'code',
                    'comments_disabled',
                    'date',
                    'dimensions',
                    'display_src',
                    'is_ad',
                    'is_video',
                    'owner',
                    'thumbnail_src',
                    'usertags',
                    'video_url',
                    'video_views',
                ])
            cls._drop_keys(
                media.get('location'), ['lat', 'lng'])
        return media

    @classmethod
    def comment(cls, comment, drop_incompat_keys=False):
        comment['created_time'] = str(int(comment['created_at']))
        from_user = {
            'id': comment['user']['id'],
            'profile_picture': comment['user'].get('profile_pic_url'),
            'username': comment['user']['username'],
            'full_name': comment['user'].get('full_name') or ''
        }
        comment['from'] = from_user
        if drop_incompat_keys:
            cls._drop_keys(comment, ['created_at', 'user'])
        return comment

    @classmethod
    def user(cls, user, drop_incompat_keys=False):
        user['bio'] = user['biography']
        user['profile_picture'] = user['profile_pic_url']
        user['website'] = user['external_url']
        counts = {
            'media': user['media']['count'],
            'followed_by': user['followed_by']['count'],
            'follows': user['follows']['count'],
        }
        user['counts'] = counts
        if drop_incompat_keys:
            cls._drop_keys(
                user,
                [
                    'biography',
                    'external_url',
                    'followed_by',
                    'follows',
                    'media',
                    'profile_pic_url',
                    'status',
                ]
            )
        return user

    @classmethod
    def list_user(cls, user, drop_incompat_keys=False):
        user['profile_picture'] = user['profile_pic_url']
        if drop_incompat_keys:
            cls._drop_keys(
                user,
                [
                    'followed_by_viewer',
                    'is_verified',
                    'profile_pic_url',
                    'requested_by_viewer',
                ]
            )
        return user
