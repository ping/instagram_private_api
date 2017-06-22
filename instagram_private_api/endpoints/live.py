from ..utils import gen_user_breadcrumb
from ..compatpatch import ClientCompatPatch


class LiveEndpointsMixin(object):
    """For endpoints in ``/live/``."""

    def user_broadcast(self, user_id):
        """
        Helper method to get a user's broadcast if there is one currently live. Returns none otherwise.

        :param user_id:
        :return:
        """
        results = self.user_story_feed(user_id)
        return results.get('broadcast')

    def broadcast_like(self, broadcast_id, like_count=1):
        """
        Like a live broadcast

        :param broadcast_id: Broadcast id
        :param like_count:
        :return:
        """
        if not 1 <= like_count <= 5:
            raise ValueError('Invalid like_count')
        broadcast_id = str(broadcast_id)
        endpoint = 'live/{broadcast_id!s}/like/'.format(**{'broadcast_id': broadcast_id})
        params = {'user_like_count': str(like_count)}
        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def broadcast_like_count(self, broadcast_id, like_ts=0):
        """
        Get a live broadcast's like count

        :param broadcast_id: Broadcast id
        :return:
        """
        broadcast_id = str(broadcast_id)
        endpoint = 'live/{broadcast_id!s}/get_like_count/'.format(**{'broadcast_id': broadcast_id})
        return self._call_api(endpoint, query={'like_ts': like_ts})

    def broadcast_comments(self, broadcast_id, last_comment_ts=0):
        """
        Get a live broadcast's latest comments

        :param broadcast_id: Broadcast id
        :param last_comment_ts:
        :return:
        """
        broadcast_id = str(broadcast_id)
        endpoint = 'live/{broadcast_id!s}/get_comment/'.format(**{'broadcast_id': broadcast_id})
        res = self._call_api(endpoint, query={'last_comment_ts': last_comment_ts})
        if self.auto_patch and res.get('comments'):
            [ClientCompatPatch.comment(c) for c in res.get('comments', [])]
            if res.get('pinned_comment'):
                ClientCompatPatch.comment(res['pinned_comment'])
        return res

    def broadcast_heartbeat_and_viewercount(self, broadcast_id):
        """
        Get a live broadcast's heartbeat and viewer count

        :param broadcast_id: Broadcast id
        :return:
        """
        broadcast_id = str(broadcast_id)
        endpoint = 'live/{broadcast_id!s}/heartbeat_and_get_viewer_count/'.format(**{'broadcast_id': broadcast_id})
        params = {
            '_csrftoken': self.csrftoken,
            '_uuid': self.uuid
        }
        return self._call_api(endpoint, params=params, unsigned=True)

    def broadcast_comment(self, broadcast_id, comment_text):
        """
        Post a comment to a live broadcast

        :param broadcast_id: Broadcast id
        :param comment_text: Comment text
        :return:
        """
        broadcast_id = str(broadcast_id)
        endpoint = 'live/{broadcast_id!s}/comment/'.format(**{'broadcast_id': broadcast_id})
        params = {
            'live_or_vod': '1',
            'offset_to_video_start': '0',
            'comment_text': comment_text,
            'user_breadcrumb': gen_user_breadcrumb(len(comment_text)),
            'idempotence_token': self.generate_uuid(),
        }
        params.update(self.authenticated_params)
        res = self._call_api(endpoint, params=params)
        if self.auto_patch and res.get('comment'):
            ClientCompatPatch.comment(res['comment'])
        return res

    def broadcast_info(self, broadcast_id):
        """
        Get broadcast information.
        Known broadcast_status values: 'active', 'interrupted', 'stopped', 'hard_stop'

        :param broadcast_id: Broadcast Id
        :return:
            .. code-block:: javascript

                {
                  "status": "ok",
                  "broadcast_status": "active",
                  "media_id": "12345678934374208_123456789",
                  "cover_frame_url": "https://scontent-hkg3-1.cdninstagram.com/something.jpg",
                  "broadcast_owner": {
                    "username": "abc",
                    "friendship_status": {
                      "incoming_request": false,
                      "followed_by": false,
                      "outgoing_request": false,
                      "following": false,
                      "blocking": false,
                      "is_private": false
                    },
                    "profile_pic_url": "http://scontent-hkg3-1.cdninstagram.com/somethingelse.jpg",
                    "profile_pic_id": "1234567850644676241_123456789",
                    "full_name": "ABC",
                    "pk": 123456789,
                    "is_verified": true,
                    "is_private": false
                  },
                  "dash_abr_playback_url": null,
                  "broadcast_message": "",
                  "published_time": 1485312576,
                  "dash_playback_url": "https://scontent-hkg3-1.cdninstagram.com/hvideo-ash1/v/dash-hd/spmething.mpd",
                  "rtmp_playback_url": "rtmp://svelivestream007.16.ash1.facebook.com:16000/live-hd/something",
                  "id": 178591123456789,
                  "viewer_count": 9000.0
                }
        """
        broadcast_id = str(broadcast_id)
        endpoint = 'live/{broadcast_id!s}/info/'.format(**{'broadcast_id': broadcast_id})
        return self._call_api(endpoint)

    def suggested_broadcasts(self, **kwargs):
        """
        Get sugggested broadcasts

        :param kwargs:
        :return:
        """
        return self._call_api('live/get_suggested_broadcasts/', query=kwargs)

    def replay_broadcast_comments(
            self, broadcast_id, starting_offset=0,
            encoding_tag='instagram_dash_remuxed'):
        """
        Get comments for a post live broadcast.

        :param broadcast_id:
        :param starting_offset:
        :param encoding_tag:
        :return:
        """
        broadcast_id = str(broadcast_id)
        query = {
            'starting_offset': starting_offset,
            'encoding_tag': encoding_tag,
        }
        endpoint = 'live/{broadcast_id!s}/get_post_live_comments/'.format(
            **{'broadcast_id': broadcast_id})
        res = self._call_api(endpoint, query=query)
        if self.auto_patch and res.get('comments'):
            [ClientCompatPatch.comment(c['comment']) for c in res.get('comments', [])
             if c.get('comment')]
        return res

    def replay_broadcast_likes(
            self, broadcast_id, starting_offset=0,
            encoding_tag='instagram_dash_remuxed'):
        """
        Get likes for a post live broadcast.

        :param broadcast_id:
        :param starting_offset:
        :param encoding_tag:
        :return:
        """
        broadcast_id = str(broadcast_id)
        query = {
            'starting_offset': starting_offset,
            'encoding_tag': encoding_tag,
        }
        endpoint = 'live/{broadcast_id!s}/get_post_live_likes/'.format(
            **{'broadcast_id': broadcast_id})
        return self._call_api(endpoint, query=query)
