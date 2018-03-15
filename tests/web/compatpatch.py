import copy
import re
import time

from ..common import WebApiTestBase, WebClientCompatPatch as ClientCompatPatch


class CompatPatchTests(WebApiTestBase):
    """Tests for ClientCompatPatch."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_compat_media',
                'test': CompatPatchTests('test_compat_media', api),
            },
            {
                'name': 'test_compat_comment',
                'test': CompatPatchTests('test_compat_comment', api),
            },
            {
                'name': 'test_compat_user',
                'test': CompatPatchTests('test_compat_user', api),
            },
            {
                'name': 'test_compat_user_list',
                'test': CompatPatchTests('test_compat_user_list', api),
                'require_auth': True,
            },
        ]

    def test_compat_media(self):
        self.api.auto_patch = False
        media = self.api.media_info2(self.test_media_shortcode)
        media_patched = copy.deepcopy(media)
        ClientCompatPatch.media(media_patched)
        self.api.auto_patch = True
        self.assertIsNone(media.get('link'))
        self.assertIsNotNone(media_patched.get('link'))
        self.assertIsNone(media.get('user'))
        self.assertIsNotNone(media_patched.get('user'))
        self.assertIsNone(media.get('type'))
        self.assertIsNotNone(media_patched.get('type'))
        self.assertIsNone(media.get('images'))
        self.assertIsNotNone(media_patched.get('images'))
        self.assertIsNone(media.get('created_time'))
        self.assertIsNotNone(media_patched.get('created_time'))
        self.assertIsNotNone(re.match(r'\d+_\d+', media_patched['id']))
        media_dropped = copy.deepcopy(media)
        ClientCompatPatch.media(media_dropped, drop_incompat_keys=True)
        self.assertIsNone(media_dropped.get('code'))
        self.assertIsNone(media_dropped.get('dimensions'))

        time.sleep(self.sleep_interval)
        # Test fix for Issue #20
        # https://github.com/ping/instagram_private_api/issues/20
        media2 = self.api.media_info2(self.test_media_shortcode2)
        ClientCompatPatch.media(media2)

    def test_compat_comment(self):
        self.api.auto_patch = False
        comment = self.api.media_comments(self.test_media_shortcode, count=1)[0]
        comment_patched = copy.deepcopy(comment)
        self.api.auto_patch = True
        ClientCompatPatch.comment(comment_patched)
        self.assertIsNone(comment.get('created_time'))
        self.assertIsNotNone(comment_patched.get('created_time'))
        self.assertIsNone(comment.get('from'))
        self.assertIsNotNone(comment_patched.get('from'))
        comment_dropped = copy.deepcopy(comment)
        ClientCompatPatch.comment(comment_dropped, drop_incompat_keys=True)
        self.assertIsNone(comment_dropped.get('created_at'))
        self.assertIsNone(comment_dropped.get('user'))

    def test_compat_user(self):
        self.api.auto_patch = False
        user = self.api.user_info2(self.test_user_name)
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.user(user_patched)
        self.api.auto_patch = True
        self.assertIsNone(user.get('bio'))
        self.assertIsNotNone(user_patched.get('bio'))
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))
        self.assertIsNone(user.get('website'))
        # no bio link for test account
        # self.assertIsNotNone(user_patched.get('website'))
        self.assertIsNone(user.get('counts'))
        self.assertIsNotNone(user_patched.get('counts'))
        user_dropped = copy.deepcopy(user)
        ClientCompatPatch.user(user_dropped, drop_incompat_keys=True)
        self.assertIsNone(user_dropped.get('biography'))
        self.assertIsNone(user_dropped.get('status'))

    def test_compat_user_list(self):
        self.api.auto_patch = False
        user = self.api.user_followers(self.test_user_id)[0]
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.list_user(user_patched)
        self.api.auto_patch = True
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))
        user_dropped = copy.deepcopy(user)
        ClientCompatPatch.list_user(user_dropped, drop_incompat_keys=True)
        self.assertIsNone(user_dropped.get('followed_by_viewer'))
        self.assertIsNone(user_dropped.get('requested_by_viewer'))
