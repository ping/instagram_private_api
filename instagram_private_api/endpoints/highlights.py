import json


class HighlightsEndpointsMixin(object):
    """For endpoints in ``/highlights/`` or related to the highlights feature."""

    def stories_archive(self, **kwargs):
        """
        Returns the authenticated user's story archive. The returned items's id
        value is passed to ``reels_media()`` to retrieve

        Example:
            .. code-block:: python

                archived_stories = api.stories_archive()
                if archived_stories.get('items):
                    item_ids = [a['id'] for a in archived_stories['items']]
                    archived_stories_media = api.reels_media(user_ids=item_ids)

        :return:
            .. code-block:: javascript

                {
                    "items": [{
                        "timestamp": 1510090000,
                        "media_count": 3,
                        "id": "archiveDay:1710000000",
                        "reel_type": "archive_day_reel",
                        "latest_reel_media": 1510090000
                    }],
                    "num_results": 1,
                    "more_available": false,
                    "max_id": null,
                    "status": "ok"
                }
        """
        query = {'include_cover': '0'}
        if kwargs:
            query.update(kwargs)
        return self._call_api('archive/reel/day_shells/', query=query)

    def highlights_user_feed(self, user_id):
        """
        Returns a user's highlight tray

        :param user_id:
        """
        endpoint = 'highlights/{user_id!s}/highlights_tray/'.format(user_id=user_id)
        return self._call_api(endpoint)

    def highlight_create(
            self, media_ids, cover_media_id=None,
            title='Highlights', source='self_profile'):
        """
        Create a new highlight

        :param media_ids: A list of media_ids
        :param cover_media_id: The media_id for the highlight cover image
        :param title: Title of the highlight
        :param module: The UI module via which the highlight is created
        """
        if not (media_ids and isinstance(media_ids, list)):
            raise ValueError('media_ids must be a non-empty list')

        if not cover_media_id:
            cover_media_id = media_ids[0]

        if not title:
            title = 'Highlights'

        if len(title) > 16:
            raise ValueError('title must not exceed 16 characters')

        cover = {
            'media_id': cover_media_id,
            'crop_rect': json.dumps(
                [0.0, 0.21830457, 1.0, 0.78094524], separators=(',', ':'))
        }
        params = {
            'media_ids': json.dumps(media_ids, separators=(',', ':')),
            'cover': json.dumps(cover, separators=(',', ':')),
            'source': source,
            'title': title,
        }
        params.update(self.authenticated_params)
        return self._call_api('highlights/create_reel/', params=params)

    def highlight_edit(
            self, highlight_id, cover_media_id=None,
            added_media_ids=[], removed_media_ids=[],
            title=None, source='story_viewer'):
        """
        Edits a highlight

        :param highlight_id: highlight_id, example 'highlight:1770000'
        :param cover_media_id: The media_id for the highlight cover image
        :param added_media_ids: List of media_id to be added
        :param removed_media_ids: List of media_id to be removed
        :param title: Title of the highlight
        :param module: The UI module via which the highlight is created
        """
        endpoint = 'highlights/{highlight_id!s}/edit_reel/'.format(
            highlight_id=highlight_id
        )

        # sanitise inputs
        if not added_media_ids:
            added_media_ids = []
        elif not isinstance(added_media_ids, list):
            raise ValueError('added_media_ids must be a list')

        if not removed_media_ids:
            removed_media_ids = []
        elif not isinstance(removed_media_ids, list):
            raise ValueError('removed_media_ids must be a list')

        if title and len(title) > 16:
            raise ValueError('title must not exceed 16 characters')

        if not (added_media_ids or removed_media_ids or cover_media_id or title):
            raise ValueError('No edited values')

        params = {
            'added_media_ids': json.dumps(added_media_ids, separators=(',', ':')),
            'removed_media_ids': json.dumps(removed_media_ids, separators=(',', ':')),
            'source': source,
        }
        if title:
            params['title'] = title
        if cover_media_id:
            cover = {
                'media_id': cover_media_id,
                'crop_rect': json.dumps(
                    [0.0, 0.21830457, 1.0, 0.78094524], separators=(',', ':'))
            }
            params['cover'] = json.dumps(cover, separators=(',', ':'))

        params.update(self.authenticated_params)
        return self._call_api(endpoint, params=params)

    def highlight_delete(self, highlight_id):
        """
        Deletes specified highlight

        :param highlight_id: highlight_id, example 'highlight:1770000'
        """
        endpoint = 'highlights/{highlight_id!s}/delete_reel/'.format(
            highlight_id=highlight_id
        )
        return self._call_api(endpoint, params=self.authenticated_params)
