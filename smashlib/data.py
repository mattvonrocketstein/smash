"""smashlib.data
"""
from smashlib.python import expanduser, opj, dirname

main_profile_name = 'SmaSh'
user_config_name = 'config.py'
SMASH_DIR = expanduser('~/.smash')
SMASH_ETC = opj(SMASH_DIR, 'etc')
SMASHLIB_DIR = dirname(__file__)
USER_CONFIG_PATH = opj(SMASH_DIR, user_config_name)
