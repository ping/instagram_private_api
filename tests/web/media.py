import unittest

from ..common import WebApiTestBase, WebClientError as ClientError, compat_mock


class MediaTests(WebApiTestBase):
    """Tests for media related functions."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_media_info',
                'test': MediaTests('test_media_info', api),
            },
            {
                'name': 'test_notfound_media_info',
                'test': MediaTests('test_notfound_media_info', api)
            },
            {
                'name': 'test_media_comments',
                'test': MediaTests('test_media_comments', api),
            },
            {
                'name': 'test_notfound_media_comments',
                'test': MediaTests('test_notfound_media_comments', api)
            },
            {
                'name': 'test_media_comments_noextract',
                'test': MediaTests('test_media_comments_noextract', api)
            },
            {
                'name': 'test_post_comment',
                'test': MediaTests('test_post_comment', api),
                'require_auth': True,
            },
            {
                'name': 'test_post_comment_mock',
                'test': MediaTests('test_post_comment_mock', api),
                'require_auth': True,
            },
            {
                'name': 'test_del_comment',
                'test': MediaTests('test_del_comment', api),
                'require_auth': True,
            },
            {
                'name': 'test_del_comment_mock',
                'test': MediaTests('test_del_comment_mock', api),
                'require_auth': True,
            },
            {
                'name': 'test_post_like',
                'test': MediaTests('test_post_like', api),
                'require_auth': True,
            },
            {
                'name': 'test_post_like_mock',
                'test': MediaTests('test_post_like_mock', api),
            },
            {
                'name': 'test_delete_like',
                'test': MediaTests('test_delete_like', api),
                'require_auth': True,
            },
            {
                'name': 'test_delete_like_mock',
                'test': MediaTests('test_delete_like_mock', api),
            },
            {
                'name': 'test_carousel_media_info',
                'test': MediaTests('test_carousel_media_info', api),
            },
            {
                'name': 'test_post_comment_validation_mock',
                'test': MediaTests('test_post_comment_validation_mock', api),
            },
            {
                'name': 'test_media_likers',
                'test': MediaTests('test_media_likers', api),
            },
            {
                'name': 'test_notfound_media_likers',
                'test': MediaTests('test_notfound_media_likers', api),
            },
            {
                'name': 'test_media_likers_noextract',
                'test': MediaTests('test_media_likers_noextract', api),
            },
        ]

    @unittest.skip('Deprecated.')
    def test_media_info(self):
        results = self.api.media_info(self.test_media_shortcode)
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('link'))
        self.assertIsNotNone(results.get('images'))

    @unittest.skip('Deprecated.')
    def test_notfound_media_info(self):
        self.assertRaises(ClientError, lambda: self.api.media_info('BSgmaRDg-xX'))

    def test_carousel_media_info(self):
        results = self.api.media_info2('BQ0eAlwhDrw')
        self.assertIsNotNone(results.get('link'))
        self.assertIsNotNone(results.get('type'))
        self.assertIsNotNone(results.get('images'))
        # Check like and comment counts are returned
        self.assertGreater(results.get('likes', {}).get('count', 0), 0)
        self.assertGreater(results.get('comments', {}).get('count', 0), 0)

    def test_media_comments(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20)
        self.assertGreaterEqual(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_notfound_media_comments(self):
        self.assertRaises(ClientError, lambda: self.api.media_comments('BSgmaRDg-xX'))

    def test_media_comments_noextract(self):
        results = self.api.media_comments(self.test_media_shortcode, count=20, extract=False)
        self.assertIsInstance(results, dict)

    def test_media_likers(self):
        results = self.api.media_likers(self.test_media_shortcode, count=20)
        self.assertGreaterEqual(len(results), 0)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_notfound_media_likers(self):
        self.assertRaises(ClientError, lambda: self.api.media_likers('BSgmaRDg-xX'))

    def test_media_likers_noextract(self):
        results = self.api.media_likers(self.test_media_shortcode, count=20, extract=False)
        self.assertIsInstance(results, dict)

    @unittest.skip('Modifies data.')
    def test_post_comment(self):
        results = self.api.post_comment(self.test_media_id, '<3')
        self.assertEqual(results.get('status'), 'ok')
        self.assertIsNotNone(results.get('id'))

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_post_comment_mock(self, make_request):
        make_request.return_value = {'status': 'ok', 'id': '12345678'}
        self.api.post_comment(self.test_media_id + '_12345', '<3')      # test sanitise media id
        make_request.assert_called_with(
            'https://www.instagram.com/web/comments/{media_id!s}/add/'.format(
                **{'media_id': self.test_media_id}),
            params={'comment_text': '<3'})

    @unittest.skip('Modifies data / Needs actual data.')
    def test_del_comment(self):
        results = self.api.delete_comment(self.test_media_id, self.test_comment_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_del_comment_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.delete_comment(self.test_media_id, self.test_comment_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/comments/{media_id!s}/delete/{comment_id!s}/'.format(
                **{'media_id': self.test_media_id, 'comment_id': self.test_comment_id}),
            params='')

    @unittest.skip('Modifies data')
    def test_post_like(self):
        results = self.api.post_like(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_post_like_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.post_like(self.test_media_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/likes/{media_id!s}/like/'.format(
                **{'media_id': self.test_media_id}),
            params='')

    @unittest.skip('Modifies data')
    def test_delete_like(self):
        results = self.api.delete_like(self.test_media_id)
        self.assertEqual(results.get('status'), 'ok')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_delete_like_mock(self, make_request):
        make_request.return_value = {'status': 'ok'}
        self.api.delete_like(self.test_media_id)
        make_request.assert_called_with(
            'https://www.instagram.com/web/likes/{media_id!s}/unlike/'.format(
                **{'media_id': self.test_media_id}),
            params='')

    @compat_mock.patch('instagram_web_api.Client._make_request')
    def test_post_comment_validation_mock(self, make_request):
        make_request.return_value = {'status': 'ok', 'id': '12345678'}

        with self.assertRaises(ValueError) as ve:
            self.api.post_comment(self.test_media_id, '.' * 400)
        self.assertEqual(str(ve.exception), 'The total length of the comment cannot exceed 300 characters.')

        with self.assertRaises(ValueError) as ve:
            self.api.post_comment(self.test_media_id, 'ABC DEFG.')
        self.assertEqual(str(ve.exception), 'The comment cannot consist of all capital letters.')

        with self.assertRaises(ValueError) as ve:
            self.api.post_comment(self.test_media_id, '#this #is #a #test #fail')
        self.assertEqual(str(ve.exception), 'The comment cannot contain more than 4 hashtags.')

        with self.assertRaises(ValueError) as ve:
            self.api.post_comment(self.test_media_id, 'https://google.com or http://instagram.com?')
        self.assertEqual(str(ve.exception), 'The comment cannot contain more than 1 URL.')
