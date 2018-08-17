import json
import re
import warnings
import time
from random import randint

from .common import ClientExperimentalWarning, MediaTypes
from ..utils import gen_user_breadcrumb
from ..compatpatch import ClientCompatPatch


class MediaEndpointsMixin(object):
    """For endpoints in ``/media/``."""

    def media_info(self, media_id):
        """
        Get media info

        :param media_id:
        :return:
        """
        endpoint = 'media/{media_id!s}/info/'.format(**{'media_id': media_id})
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def medias_info(self, media_ids):
        """
        Get multiple media infos

        :param media_ids: list of media ids
        :return:
        """

        if isinstance(media_ids, str):
            media_ids = [media_ids]

        params = {
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken,
            'media_ids': ','.join(media_ids),
            'ranked_content': 'true',
            'include_inactive_reel': 'true',
        }
        res = self._call_api('media/infos/', query=params)
        if self.auto_patch:
            [ClientCompatPatch.media(m, drop_incompat_keys=self.drop_incompat_keys)
             for m in res.get('items', [])]
        return res

    def media_permalink(self, media_id):
        """
        Get media permalink

        :param media_id:
        :return:
        """
        endpoint = 'media/{media_id!s}/permalink/'.format(**{'media_id': media_id})
        res = self._call_api(endpoint)
        return res

    def media_comments(self, media_id, **kwargs):
        """
        Get media comments. Fixed at 20 comments returned per page.

        :param media_id: Media id
        :param kwargs:
            **max_id**: For pagination
        :return:
        """
        endpoint = 'media/{media_id!s}/comments/'.format(**{'media_id': media_id})
        query = {
            'can_support_threading': 'true'
        }
        if kwargs:
            query.update(kwargs)
        res = self._call_api(endpoint, query=query)

        if self.auto_patch:
            [ClientCompatPatch.comment(c, drop_incompat_keys=self.drop_incompat_keys)
             for c in res.get('comments', [])]
            [ClientCompatPatch.comment(c, drop_incompat_keys=self.drop_incompat_keys)
             for c in res.get('preview_comments', [])]
        return res

    def media_n_comments(self, media_id, n=150, reverse=False, **kwargs):
        """
        Helper method to retrieve n number of comments for a media id

        :param media_id: Media id
        :param n: Minimum number of comments to fetch
        :param reverse: Reverse list of comments (ordered by created_time)
        :param kwargs:
        :return:
        """

        endpoint = 'media/{media_id!s}/comments/'.format(**{'media_id': media_id})

        comments = []
        results = self._call_api(endpoint, query=kwargs)
        comments.extend(results.get('comments', []))

        while (((results.get('has_more_comments') and results.get('next_max_id'))
                or (results.get('has_more_headload_comments') and results.get('next_min_id')))
                and len(comments) < n):

            if results.get('has_more_comments'):
                kwargs.update({'max_id': results.get('next_max_id')})
            else:
                kwargs.update({'min_id': results.get('next_min_id')})

            results = self._call_api(endpoint, query=kwargs)
            comments.extend(results.get('comments', []))
            if not (results.get('next_max_id') or results.get('next_min_id') or results.get('comments')):
                # bail out if no max_id/min_id or comments returned
                break

        if self.auto_patch:
            [ClientCompatPatch.comment(c, drop_incompat_keys=self.drop_incompat_keys)
             for c in comments]

        return sorted(comments, key=lambda k: k['created_at_utc'], reverse=reverse)

    def comment_replies(self, media_id, comment_id, **kwargs):
        """
        Get comment replies. Fixed at 20 replies returned per page.
        Check for 'has_more_tail_child_comments', 'next_max_child_cursor' to determine
        if there are more replies to page through.

        :param media_id: Media id
        :param comment_id: Comment id
        :param kwargs:
            **max_id**: For pagination
        :return:
        """
        endpoint = 'media/{media_id!s}/comments/{comment_id!s}/child_comments/'.format(
            **{'media_id': media_id, 'comment_id': comment_id})
        res = self._call_api(endpoint, query=kwargs)

        if self.auto_patch:
            [ClientCompatPatch.comment(c, drop_incompat_keys=self.drop_incompat_keys)
             for c in res.get('child_comments', [])]
            ClientCompatPatch.comment(res.get('parent_comment'))
        return res

    def comment_inline_replies(self, media_id, comment_id, max_id, **kwargs):
        """
        Get inline comment replies.
        Check for 'next_max_child_cursor' from ``media_comments()``
        to determine if there are inline comment replies to retrieve.

        :param media_id: Media id
        :param comment_id: Comment id
        :param max_id: The comment's 'next_max_child_cursor' value from``media_comments()``
        :return:
        """
        endpoint = 'media/{media_id!s}/comments/{comment_id!s}/inline_child_comments/'.format(
            **{'media_id': media_id, 'comment_id': comment_id})
        query = {'max_id': max_id}
        if kwargs:
            query.update(kwargs)
        res = self._call_api(endpoint, query=query)
        if self.auto_patch:
            [ClientCompatPatch.comment(c, drop_incompat_keys=self.drop_incompat_keys)
             for c in res.get('child_comments', [])]
            ClientCompatPatch.comment(res.get('parent_comment'))
        return res

    def edit_media(self, media_id, caption, usertags=None):
        """
        Edit a media's caption

        :param media_id: Media id
        :param caption: Caption text
        :param usertags: array of user_ids and positions in the format below:

            .. code-block:: javascript

                usertags = [
                    {"user_id":4292127751, "position":[0.625347,0.4384531]}
                ]
        :return:
        """
        if usertags is None:
            usertags = []
        endpoint = 'media/{media_id!s}/edit_media/'.format(**{'media_id': media_id})
        params = {'caption_text': caption}
        params.update(self.authenticated_params)
        if usertags:
            utags = {'in': [{'user_id': u['user_id'], 'position': u['position']} for u in usertags]}
            params['usertags'] = json.dumps(utags, separators=(',', ':'))
        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            ClientCompatPatch.media(res.get('media'))
        return res

    def delete_media(self, media_id):
        """
        Delete a media

        :param media_id: Media id
        :return:
            .. code-block:: javascript

                {"status": "ok", "did_delete": true}
        """
        endpoint = 'media/{media_id!s}/delete/'.format(**{'media_id': media_id})
        params = {'media_id': media_id}
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def post_comment(self, media_id, comment_text):
        """
        Post a comment.
        Comment text validation according to https://www.instagram.com/developer/endpoints/comments/#post_media_comments

        :param media_id: Media id
        :param comment_text: Comment text
        :return:
            .. code-block:: javascript

                {
                  "comment": {
                    "status": "Active",
                    "media_id": 123456789,
                    "text": ":)",
                    "created_at": 1479453671.0,
                    "user": {
                      "username": "x",
                      "has_anonymous_profile_picture": false,
                      "profile_pic_url": "http://scontent-sit4-1.cdninstagram.com/abc.jpg",
                      "full_name": "x",
                      "pk": 123456789,
                      "is_verified": false,
                      "is_private": false
                    },
                    "content_type": "comment",
                    "created_at_utc": 1479482471,
                    "pk": 17865505612040669,
                    "type": 0
                  },
                  "status": "ok"
                }
        """

        if len(comment_text) > 300:
            raise ValueError('The total length of the comment cannot exceed 300 characters.')
        if re.search(r'[a-z]+', comment_text, re.IGNORECASE) and comment_text == comment_text.upper():
            raise ValueError('The comment cannot consist of all capital letters.')
        if len(re.findall(r'#[^#]+\b', comment_text, re.UNICODE | re.MULTILINE)) > 4:
            raise ValueError('The comment cannot contain more than 4 hashtags.')
        if len(re.findall(r'\bhttps?://\S+\.\S+', comment_text)) > 1:
            raise ValueError('The comment cannot contain more than 1 URL.')

        endpoint = 'media/{media_id!s}/comment/'.format(**{'media_id': media_id})
        params = {
            'comment_text': comment_text,
            'user_breadcrumb': gen_user_breadcrumb(len(comment_text)),
            'idempotence_token': self.generate_uuid(),
            'containermodule': 'comments_feed_timeline',
            'radio_type': self.radio_type,
        }
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch:
            ClientCompatPatch.comment(res['comment'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def delete_comment(self, media_id, comment_id):
        """
        Delete a comment

        :param media_id: Media id
        :param comment_id: Comment id
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{media_id!s}/comment/{comment_id!s}/delete/'.format(**{
            'media_id': media_id, 'comment_id': comment_id})
        params = {}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def bulk_delete_comments(self, media_id, comment_ids):
        """
        Bulk delete comment

        :param media_id: Media id
        :param comment_ids: List of comment ids
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        if not isinstance(comment_ids, list):
            comment_ids = [comment_ids]
        endpoint = 'media/{media_id!s}/comment/bulk_delete/'.format(**{
            'media_id': media_id})
        params = {
            'comment_ids_to_delete': ','.join(
                [str(comment_id) for comment_id in comment_ids])
        }
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def media_likers(self, media_id, **kwargs):
        """
        Get users who have liked a post

        :param media_id:
        :return:
        """
        endpoint = 'media/{media_id!s}/likers/'.format(**{'media_id': media_id})
        res = self._call_api(endpoint, query=kwargs)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def media_likers_chrono(self, media_id):
        """
        EXPERIMENTAL ENDPOINT, INADVISABLE TO USE.
        Get users who have liked a post in chronological order

        :param media_id:
        :return:
        """
        warnings.warn('This endpoint is experimental. Do not use.', ClientExperimentalWarning)
        res = self._call_api('media/{media_id!s}/likers_chrono/'.format(**{'media_id': media_id}))
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def post_like(self, media_id, module_name='feed_timeline'):
        """
        Like a post

        :param media_id: Media id
        :param module_name: Example: 'feed_timeline', 'video_view', 'photo_view'
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{media_id!s}/like/'.format(**{'media_id': media_id})
        params = {
            'media_id': media_id,
            'module_name': module_name,
            'radio_type': self.radio_type,
        }
        params.update(self.authenticated_params)
        # d query param = flag for double tap
        res = self._call_api(endpoint, params=params, query={'d': '1'})
        return res

    def delete_like(self, media_id, module_name='feed_timeline'):
        """
        Unlike a post

        :param media_id:
        :param module_name: Example: 'feed_timeline', 'video_view', 'photo_view'
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{media_id!s}/unlike/'.format(**{'media_id': media_id})
        params = {
            'media_id': media_id,
            'module_name': module_name,
            'radio_type': self.radio_type,
        }
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        return res

    def media_seen(self, reels):
        """
        Mark multiple stories as seen

        :param reels: A list of reel media objects, or a dict of media_ids and timings
            as defined below.

            .. code-block:: javascript

                {
                    "1309763051087626108_124317_124317": ["1470355944_1470372029"],
                    "1309764045355643149_124317_124317": ["1470356063_1470372039"],
                    "1309818450243415912_124317_124317": ["1470362548_1470372060"],
                    "1309764653429046112_124317_124317": ["1470356135_1470372049"],
                    "1309209597843679372_124317_124317": ["1470289967_1470372013"]
                }

                where
                    1309763051087626108_124317 = <media_id>,
                    124317 = <media.owner_id>
                    1470355944_1470372029 is <media_created_time>_<view_time>

        :return:
        """
        if isinstance(reels, list):
            # is a list of reel media
            reels_seen = {}
            reels = sorted(reels, key=lambda m: m['taken_at'], reverse=True)
            now = int(time.time())
            for i, reel in enumerate(reels):
                reel_seen_at = now - min(i + 1 + randint(0, 2), max(0, now - reel['taken_at']))
                reels_seen['{0!s}_{1!s}'.format(reel['id'], reel['user']['pk'])] = [
                    '{0!s}_{1!s}'.format(reel['taken_at'], reel_seen_at)]
            params = {'reels': reels_seen}
        else:
            params = {'reels': reels}
        params.update(self.authenticated_params)
        res = self._call_api('media/seen/', params=params, version='v2')
        return res

    def comment_like(self, comment_id):
        """
        Like a comment

        :param comment_id:

        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{comment_id!s}/comment_like/'.format(**{'comment_id': comment_id})
        params = self.authenticated_params
        return self._call_api(endpoint, params=params)

    def comment_likers(self, comment_id):
        """
        Get users who have liked a comment

        :param comment_id:
        :return:
        """
        endpoint = 'media/{comment_id!s}/comment_likers/'.format(**{'comment_id': comment_id})
        res = self._call_api(endpoint)
        if self.auto_patch:
            [ClientCompatPatch.list_user(u, drop_incompat_keys=self.drop_incompat_keys)
             for u in res.get('users', [])]
        return res

    def comment_unlike(self, comment_id):
        """
        Unlike a comment

        :param comment_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{comment_id!s}/comment_unlike/'.format(**{'comment_id': comment_id})
        params = self.authenticated_params
        return self._call_api(endpoint, params=params)

    def save_photo(self, media_id, added_collection_ids=None):
        """
        Save a photo

        :param media_id: Media id
        :param added_collection_ids: optional list of collection IDs to add the media to
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{media_id!s}/save/'.format(**{'media_id': media_id})
        params = {'radio_type': self.radio_type}
        if added_collection_ids:
            if isinstance(added_collection_ids, str):
                added_collection_ids = [added_collection_ids]
            params['added_collection_ids'] = json.dumps(added_collection_ids, separators=(',', ':'))
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def unsave_photo(self, media_id, removed_collection_ids=None):
        """
        Unsave a photo

        :param media_id:
        :param removed_collection_ids: optional list of collection IDs to remove the media from
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{media_id!s}/unsave/'.format(**{'media_id': media_id})
        params = {'radio_type': self.radio_type}
        if removed_collection_ids:
            if isinstance(removed_collection_ids, str):
                removed_collection_ids = [removed_collection_ids]
            params['removed_collection_ids'] = json.dumps(removed_collection_ids, separators=(',', ':'))
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def disable_comments(self, media_id):
        """
        Disable comments for a media

        :param media_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        endpoint = 'media/{media_id!s}/disable_comments/'.format(**{'media_id': media_id})
        params = {
            '_csrftoken': self.csrftoken,
            '_uuid': self.uuid,
        }
        res = self._call_api(endpoint, params=params, unsigned=True)
        return res

    def enable_comments(self, media_id):
        """
        Enable comments for a media

        :param media_id:
        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """

        endpoint = 'media/{media_id!s}/enable_comments/'.format(**{'media_id': media_id})
        params = {
            '_csrftoken': self.csrftoken,
            '_uuid': self.uuid,
        }
        res = self._call_api(endpoint, params=params, unsigned=True)
        return res

    def media_only_me(self, media_id, media_type, undo=False):
        """
        Archive/unarchive a media so that it is only viewable by the owner.

        :param media_id:
        :param media_type: One of :attr:`MediaTypes.PHOTO`, :attr:`MediaTypes.VIDEO`, or :attr:`MediaTypes.CAROUSEL`
        :param undo: bool

        :return:
            .. code-block:: javascript

                {"status": "ok"}
        """
        if media_type not in MediaTypes.ALL:
            raise ValueError('Invalid media type.')

        endpoint = 'media/{media_id!s}/{only_me!s}/'.format(**{
            'media_id': media_id,
            'only_me': 'only_me' if not undo else 'undo_only_me'
        })
        params = {'media_id': media_id}
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params, query={'media_type': media_type})
        return res

    def media_undo_only_me(self, media_id, media_type):
        """
        Undo making a media only me.

        :param media_id:
        :param media_type: One of :attr:`MediaTypes.PHOTO`, :attr:`MediaTypes.VIDEO`, or :attr:`MediaTypes.CAROUSEL`
        """
        return self.media_only_me(media_id, media_type, undo=True)

    def story_viewers(self, story_pk, **kwargs):
        """
        Get list of story viewers

        :param story_pk: Story media's PK identifier, e.g. "1700000123"
        :param kwargs:
            **max_id**: For pagination
        :return:
        """
        endpoint = 'media/{story_pk!s}/list_reel_media_viewer/'.format(
            story_pk=story_pk)
        return self._call_api(endpoint, query=kwargs)
