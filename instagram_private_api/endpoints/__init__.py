# flake8: noqa
from .accounts import AccountsEndpointsMixin
from .discover import DiscoverEndpointsMixin
from .feed import FeedEndpointsMixin
from .friendships import FriendshipsEndpointsMixin
from .live import LiveEndpointsMixin
from .media import MediaEndpointsMixin
from .misc import MiscEndpointsMixin
from .locations import LocationsEndpointsMixin
from .tags import TagsEndpointsMixin
from .upload import UploadEndpointsMixin
from .users import UsersEndpointsMixin
from .usertags import UsertagsEndpointsMixin
from .collections import CollectionsEndpointsMixin
from .highlights import HighlightsEndpointsMixin
from .igtv import IGTVEndpointsMixin

from .common import (
    ClientDeprecationWarning,
    ClientPendingDeprecationWarning,
    ClientExperimentalWarning,
)
