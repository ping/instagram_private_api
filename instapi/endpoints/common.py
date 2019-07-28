
class ClientDeprecationWarning(DeprecationWarning):
    pass


class ClientPendingDeprecationWarning(PendingDeprecationWarning):
    pass


class ClientExperimentalWarning(UserWarning):
    pass


class MediaTypes(object):
    """Psuedo enum-ish/lookup class for media types."""

    PHOTO = 1       #: Photo type
    VIDEO = 2       #: Video type
    CAROUSEL = 8    #: Carousel/Album type

    ALL = (PHOTO, VIDEO, CAROUSEL)

    __media_type_map = {
        'image': PHOTO,
        'video': VIDEO,
        'carousel': CAROUSEL,
    }

    @staticmethod
    def id_to_name(media_type_id):
        """Convert a media type ID to its name"""
        try:
            return [k for k, v in MediaTypes.__media_type_map.items() if v == media_type_id][0]
        except IndexError:
            raise ValueError('Invalid media ID')

    @staticmethod
    def name_to_id(media_type_name):
        """Convert a media type name to its ID"""
        try:
            return MediaTypes.__media_type_map[media_type_name]
        except KeyError:
            raise ValueError('Invalid media name')
