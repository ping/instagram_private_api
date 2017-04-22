
from ..common import (
    ApiTestBase, Client, ClientLoginRequiredError, Constants,
    gen_user_breadcrumb, max_chunk_size_generator, max_chunk_count_generator,
    compat_mock
)


class ClientTests(ApiTestBase):

    @classmethod
    def init_all(cls, api):
        return [
            {
                'name': 'test_validate_useragent',
                'test': ClientTests('test_validate_useragent', api)
            },
            {
                'name': 'test_validate_useragent2',
                'test': ClientTests('test_validate_useragent2', api)
            },
            {
                'name': 'test_generate_useragent',
                'test': ClientTests('test_generate_useragent', api)
            },
            {
                'name': 'test_cookiejar_dump',
                'test': ClientTests('test_cookiejar_dump', api)
            },
            {
                'name': 'test_gen_user_breadcrumb',
                'test': ClientTests('test_gen_user_breadcrumb', api)
            },
            {
                'name': 'test_max_chunk_size_generator',
                'test': ClientTests('test_max_chunk_size_generator', api)
            },
            {
                'name': 'test_max_chunk_count_generator',
                'test': ClientTests('test_max_chunk_count_generator', api)
            },
            {
                'name': 'test_settings',
                'test': ClientTests('test_settings', api)
            },
            {
                'name': 'test_user_agent',
                'test': ClientTests('test_user_agent', api)
            },
            {
                'name': 'test_client_properties',
                'test': ClientTests('test_client_properties', api)
            },
            {
                'name': 'test_client_loginrequired',
                'test': ClientTests('test_client_loginrequired', api)
            },
        ]

    def test_validate_useragent(self):
        ua = 'Instagram 9.2.0 Android (22/5.1.1; 480dpi; 1080x1920; Xiaomi; Redmi Note 3; kenzo; qcom; en_GB)'
        results = Client.validate_useragent(ua)
        self.assertEqual(results['parsed_params']['brand'], 'Xiaomi')
        self.assertEqual(results['parsed_params']['device'], 'Redmi Note 3')
        self.assertEqual(results['parsed_params']['model'], 'kenzo')
        self.assertEqual(results['parsed_params']['resolution'], '1080x1920')
        self.assertEqual(results['parsed_params']['dpi'], '480dpi')
        self.assertEqual(results['parsed_params']['chipset'], 'qcom')
        self.assertEqual(results['parsed_params']['android_version'], 22)
        self.assertEqual(results['parsed_params']['android_release'], '5.1.1')
        self.assertEqual(results['parsed_params']['app_version'], '9.2.0')

    def test_validate_useragent2(self):
        ua = 'Instagram 9.2.0 Android (xx/5.1.1; 480dpi; 1080x1920; Xiaomi; Redmi Note 3; kenzo; qcom; en_GB)'
        with self.assertRaises(ValueError):
            Client.validate_useragent(ua)

    def test_generate_useragent(self):
        custom_device = {
            'manufacturer': 'Samsung',
            'model': 'maguro',
            'device': 'Galaxy Nexus',
            'android_release': '4.3',
            'android_version': 18,
            'dpi': '320dpi',
            'resolution': '720x1280',
            'chipset': 'qcom'
        }
        custom_ua = Client.generate_useragent(
            android_release=custom_device['android_release'],
            android_version=custom_device['android_version'],
            phone_manufacturer=custom_device['manufacturer'],
            phone_device=custom_device['device'],
            phone_model=custom_device['model'],
            phone_dpi=custom_device['dpi'],
            phone_resolution=custom_device['resolution'],
            phone_chipset=custom_device['chipset']
        )
        self.assertEqual(
            custom_ua,
            'Instagram %s Android (%s/%s; %s; %s; '
            '%s; %s; %s; %s; en_US)'
            % (
                Constants.APP_VERSION,
                custom_device['android_version'],
                custom_device['android_release'],
                custom_device['dpi'],
                custom_device['resolution'],
                custom_device['manufacturer'],
                custom_device['device'],
                custom_device['model'],
                custom_device['chipset'],
            )
        )

    def test_cookiejar_dump(self):
        dump = self.api.cookie_jar.dump()
        self.assertIsNotNone(dump)

    def test_gen_user_breadcrumb(self):
        output = gen_user_breadcrumb(15)
        self.assertIsNotNone(output)

    def test_max_chunk_size_generator(self):
        chunk_data = 'abcdefghijklmnopqrstuvwxyz'
        chunk_size = 5
        chunk_count = 0
        for chunk_info, data in max_chunk_size_generator(chunk_size, chunk_data):
            chunk_count += 1
            self.assertIsNotNone(data, 'Empty chunk.')
            self.assertLessEqual(len(data), chunk_size, 'Chunk size is too big.')
            self.assertEqual(len(data), chunk_info.length, 'Chunk length is wrong.')
            self.assertEqual(chunk_info.is_first, chunk_count == 1)

    def test_max_chunk_count_generator(self):
        chunk_data = 'abcdefghijklmnopqrstuvwxyz'
        expected_chunk_count = 5
        chunk_count = 0
        for chunk_info, data in max_chunk_count_generator(expected_chunk_count, chunk_data):
            chunk_count += 1
            self.assertIsNotNone(data, 'Empty chunk.')
            self.assertEqual(len(data), chunk_info.length, 'Chunk length is wrong.')
            self.assertEqual(chunk_info.is_first, chunk_count == 1)
            self.assertEqual(chunk_info.is_last, chunk_count == expected_chunk_count)

        self.assertEqual(chunk_count, expected_chunk_count, 'Chunk count is wrong.')

    def test_settings(self):
        results = self.api.settings
        for k in ('uuid', 'device_id', 'ad_id', 'signature_key', 'key_version',
                  'ig_capabilities', 'app_version', 'android_release', 'android_version',
                  'phone_manufacturer', 'phone_device', 'phone_model', 'phone_dpi', 'phone_resolution',
                  'phone_chipset', 'cookie', 'created_ts'):
            self.assertIsNotNone(results.get(k))

    def test_user_agent(self):
        ua = self.api.user_agent
        self.assertIsNotNone(ua)
        self.api.user_agent = ua

        def test_ua_setter():
            self.api.user_agent = 'Agent X'
        self.assertRaises(ValueError, test_ua_setter)

        custom_ua = self.api.generate_useragent(phone_manufacturer='BrandX')
        self.assertTrue('BrandX' in custom_ua)

        results = self.api.validate_useragent(custom_ua)
        self.assertEqual(results['parsed_params']['brand'], 'BrandX')

    def test_client_properties(self):
        results = self.api.get_cookie_value('non-existent-cookie-value')
        self.assertIsNone(results)

        self.assertIsNotNone(self.api.csrftoken)
        self.assertIsNotNone(self.api.token)
        self.assertIsNotNone(self.api.authenticated_user_id)
        self.assertIsNotNone(self.api.authenticated_user_name)
        self.assertIsNotNone(self.api.rank_token)
        self.assertIsNotNone(self.api.phone_id)
        self.assertIsNotNone(self.api.radio_type)
        self.assertIsNotNone(self.api.generate_deviceid())
        self.assertIsInstance(self.api.timezone_offset, int)

    def test_client_loginrequired(self):
        with self.assertRaises(ClientLoginRequiredError):
            Client('', '')
