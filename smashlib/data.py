"""smashlib.data
"""

import os

expanduser = os.path.expanduser

main_profile_name = 'SmaSh'
user_config_name = 'config.py'
SMASH_DIR = expanduser('~/.smash')
SMASHLIB_DIR = os.path.dirname(__file__)
USER_CONFIG_PATH = os.path.join(SMASH_DIR, user_config_name)
