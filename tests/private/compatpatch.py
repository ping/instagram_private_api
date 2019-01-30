import copy

from ..common import ApiTestBase, ClientCompatPatch


class CompatPatchTests(ApiTestBase):
    """Tests for the ClientCompatPatch class."""

    @staticmethod
    def init_all(api):
        test_media_id = '1962809196194057623_25025320'
        return [
            {
                'name': 'test_compat_media',
                'test': CompatPatchTests('test_compat_media', api, media_id=test_media_id)
            },
            {
                'name': 'test_compat_comment',
                'test': CompatPatchTests('test_compat_comment', api, media_id=test_media_id)
            },
            {
                'name': 'test_compat_user',
                'test': CompatPatchTests('test_compat_user', api, user_id='124317')
            },
            {
                'name': 'test_compat_user_list',
                'test': CompatPatchTests('test_compat_user_list', api, user_id='124317')
            },
        ]

    def test_compat_media(self):
        self.api.auto_patch = False
        results = self.api.media_info(self.test_media_id)
        self.api.auto_patch = True
        media = results.get('items', [])[0]
        media_patched = copy.deepcopy(media)
        ClientCompatPatch.media(media_patched)

        self.assertIsNone(media.get('link'))
        self.assertIsNotNone(media_patched.get('link'))
        self.assertIsNone(media.get('created_time'))
        self.assertIsNotNone(media_patched.get('created_time'))
        self.assertIsNone(media.get('images'))
        self.assertIsNotNone(media_patched.get('images'))
        self.assertIsNone(media.get('type'))
        self.assertIsNotNone(media_patched.get('type'))
        self.assertIsNone(media.get('filter'))
        self.assertIsNotNone(media_patched.get('filter'))
        self.assertIsNone(media.get('user', {}).get('id'))
        self.assertIsNotNone(media_patched.get('user', {}).get('id'))
        self.assertIsNone(media.get('user', {}).get('profile_picture'))
        self.assertIsNotNone(media_patched.get('user', {}).get('profile_picture'))
        if media['caption']:
            self.assertIsNone(media.get('caption', {}).get('id'))
            self.assertIsNotNone(media_patched['caption']['id'])
            self.assertIsNone(media.get('caption', {}).get('from'))
            self.assertIsNotNone(media_patched['caption']['from'])
        media_dropped = copy.deepcopy(media)
        ClientCompatPatch.media(media_dropped, drop_incompat_keys=True)
        self.assertIsNone(media_dropped.get('pk'))

    def test_compat_comment(self):
        self.api.auto_patch = False
        results = self.api.media_comments(self.test_media_id)
        self.api.auto_patch = True
        self.assertGreater(len(results.get('comments', [])), 0, 'No items returned.')
        comment = results.get('comments', [{}])[0]
        comment_patched = copy.deepcopy(comment)
        ClientCompatPatch.comment(comment_patched)
        self.assertIsNone(comment.get('id'))
        self.assertIsNotNone(comment_patched.get('id'))
        self.assertIsNone(comment.get('created_time'))
        self.assertIsNotNone(comment_patched.get('created_time'))
        self.assertIsNone(comment.get('from'))
        self.assertIsNotNone(comment_patched.get('from'))

        comment_dropped = copy.deepcopy(comment)
        ClientCompatPatch.comment(comment_dropped, drop_incompat_keys=True)
        self.assertIsNone(comment_dropped.get('pk'))

    def test_compat_user(self):
        self.api.auto_patch = False
        results = self.api.user_info(self.test_user_id)
        self.api.auto_patch = True
        user = results.get('user', {})
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.user(user_patched)
        self.assertIsNone(user.get('id'))
        self.assertIsNotNone(user_patched.get('id'))
        self.assertIsNone(user.get('bio'))
        self.assertIsNotNone(user_patched.get('bio'))
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))
        self.assertIsNone(user.get('website'))
        self.assertIsNotNone(user_patched.get('website'))

        user_dropped = copy.deepcopy(user)
        ClientCompatPatch.user(user_dropped, drop_incompat_keys=True)
        self.assertIsNone(user_dropped.get('pk'))

    def test_compat_user_list(self):
        self.api.auto_patch = False
        rank_token = self.api.generate_uuid()
        results = self.api.user_following(self.test_user_id, rank_token)
        self.api.auto_patch = True
        user = results.get('users', [{}])[0]
        user_patched = copy.deepcopy(user)
        ClientCompatPatch.list_user(user_patched)
        self.assertIsNone(user.get('id'))
        self.assertIsNotNone(user_patched.get('id'))
        self.assertIsNone(user.get('profile_picture'))
        self.assertIsNotNone(user_patched.get('profile_picture'))

        user_dropped = copy.deepcopy(user)
        ClientCompatPatch.list_user(user_dropped, drop_incompat_keys=True)
        self.assertIsNone(user_dropped.get('pk'))
