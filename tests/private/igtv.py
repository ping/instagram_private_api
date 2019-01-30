
from ..common import ApiTestBase


class IGTVTests(ApiTestBase):
    """Tests for IGTVEndpointsMixin."""

    @staticmethod
    def init_all(api):
        return [
            {
                'name': 'test_tvchannel',
                'test': IGTVTests('test_tvchannel', api)
            },
            {
                'name': 'test_tvguide',
                'test': IGTVTests('test_tvguide', api)
            },
            {
                'name': 'test_search_igtv',
                'test': IGTVTests('test_search_igtv', api)
            },
        ]

    def test_tvchannel(self):
        results = self.api.tvchannel('for_you')
        self.assertGreater(len(results.get('items', [])), 0)

    def test_tvguide(self):
        results = self.api.tvguide()
        self.assertGreater(len(results.get('channels', [])), 0)

    def test_search_igtv(self):
        results = self.api.search_igtv('cooking')
        self.assertGreater(len(results.get('results', [])), 0)
