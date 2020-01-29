# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Accessing variables.
user_name = os.getenv('INSTAGRAM_USERNAME')
password = os.getenv('INSTAGRAM_PASSWORD')

# Using variables.
print(user_name)
print(password)






# # from instagram_private_api import Client, ClientCompatPatch
# # api = Client(user_name, password)

# NOTES....
# from instagram_web_api import Client, ClientCompatPatch, ClientError, ClientLoginError
# # rhx_gis = "4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178" # self._extract_rhx_gis(init_res_content) or
# web_api = Client(auto_patch=True, drop_incompat_keys=False, rhx_gis = "4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178")
# user_feed_info = web_api.user_feed('329452045', count=10)
# for post in user_feed_info:
#     print('%s from %s' % (post['link'], post['user']['username']))
