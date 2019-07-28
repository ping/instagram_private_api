import json


class InsightsEndpointsMixin(object):
    """For endpoints in related to insights functionality."""

    def insights(self):
        """
        Get insights
        :param day:
        :return:
        """

        params = {
            'locale': 'en_US',
            'vc_policy': 'insights_policy',
            'surface': 'account',
            'access_token': 'undefined',
            'fb_api_caller_class': 'RelayModern',
            'variables': json.dumps({
                'IgInsightsGridMediaImage_SIZE': 240,
                'timezone': 'Asia/Jakarta',
                'activityTab': 'true',
                'audienceTab': 'true',
                'contentTab': 'true',
                'query_params': json.dumps({
                    'access_token': '',
                    'id': self.authenticated_user_id
                })
            }),
            'doc_id': '1926322010754880'
        }
        res = self._call_api('ads/graphql/', query=params, unsigned=True)
        return res
