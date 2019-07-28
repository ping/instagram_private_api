import json


class AddressBookEndpointMixin(object):
    """For endpoints in ``/address_book/``."""

    def link(self, contacts, **kwargs):
        """
        Sync contacts with instagram app

        :param contacts: list of contact entities. Examples:
            {
                'first_name': 'khatam_testing',
                'phone_numbers': ['+989395405909'],
                'email_addresses': ['khatam_testing@gmail.com']
            },

        :return:
            - list of user accounts created based on contacts
        """

        endpoint = 'address_book/link/'
        params = {
            'contacts': json.dumps(contacts),
            '_uuid': self.uuid,
            '_csrftoken': self.csrftoken
        }
        if kwargs:
            params.update(kwargs)
        return self._call_api(endpoint, params=params, unsigned=True)

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
        return self._call_api(endpoint, params=params, unsigned=True)
