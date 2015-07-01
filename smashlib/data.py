"""smashlib.data
"""
import os
from goulash.python import expanduser, opj, dirname
from goulash._os import home

main_profile_name = 'SmaSh'
user_config_name = 'config.py'
SMASH_DIR = expanduser('~/.smash')
SMASH_BIN = os.path.join(SMASH_DIR, 'bin')
SMASH_LOGS = os.path.join(SMASH_DIR, 'logs')
SMASH_ETC = os.path.join(SMASH_DIR, 'etc')
SMASHLIB_DIR = dirname(__file__)
USER_CONFIG_PATH = os.path.join(SMASH_DIR, user_config_name)
ALIAS_CONFIG_PATH = os.path.join(SMASH_ETC, 'aliases.json')
MACRO_CONFIG_PATH = os.path.join(SMASH_ETC, 'macros.json')
EDITOR_CONFIG_PATH = os.path.join(SMASH_ETC, 'editor.json')
ENV_CONFIG_PATH = os.path.join(SMASH_ETC, 'env.json')
PROMPT_CONFIG_PATH = os.path.join(SMASH_ETC, 'prompt.json')

P_CODE_FILE = {
    '.py': 'python',
    '.pp': 'puppet',
    '.md': 'docs',
    '.rst': 'docs',
    '.hs': 'haskell',
    'Vagrantfile': 'vagrant',
    'tox.ini': 'tox',
}
"""
lcfg =  {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'django.request': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False
        },
    }
}
"""
