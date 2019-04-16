import warnings

from .common import ClientDeprecationWarning
from ..compatpatch import ClientCompatPatch
from ..compat import compat_urllib_parse
from ..utils import raise_if_invalid_rank_token


class AddressBookEndpointMixin(object):
    """For endpoints in ``/address_book/``."""

    def link(self, kwargs):
        """
        Sync contacts with instagram for khatam perpose

        :param kwargs:
           - **contacts**: list of contact entities. Examples:
            {
                'first_name': 'khatam_testing',
                'phone_numbers': ['+989395405909'],
                'email_addresses': ['khatam_testing@gmail.com']
            },

        :return:
            - list of users created based on contacts
        """

        endpoint ='address_book/link/'
        params = {
            'contacts': json.dumps(contacts),
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken
        }
        return api._call_api('address_book/link/', params=data, unsigned=True)

    def unlink(self):
        """
        Unsync contacts with instagram

        :return:
            - list of users created based on contacts
        """
        endpoint = 'address_book/unlink/'
        params = {
                    '_uid': self.authenticated_user_id,
                    '_uuid': self.uuid,
                    '_csrftoken': self.csrftoken
                }
        return api._call_api('address_book/link/', params=data, unsigned=True)