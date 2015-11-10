"""smashlib.data
"""
import os

from goulash.python import dirname
from goulash.python import expanduser

main_profile_name = 'SmaSh'
fname_user_config = 'config.py'
fname_editor_config = 'editor.json'

LOG_FORMAT_DEFAULT = ('[%(name)s:%(levelname)s:%(process)d] '
           '%(pathname)s:%(lineno)-4d'
           ' - %(funcName)s:\n  %(message)s')

LOG_HANDLER_DEFAULTS = {
    'class': 'logging.handlers.RotatingFileHandler',
    'level': 'INFO',
    'formatter': 'detailed',
    'mode': 'a',
    'maxBytes': 10485760,
    'backupCount': 3, }

SMASH_DIR = expanduser('~/.smash')
SMASH_BIN = os.path.join(SMASH_DIR, 'bin')
D_SMASH_LOGS = os.path.join(SMASH_DIR, 'logs')
DIR_SMASH_ETC = os.path.join(SMASH_DIR, 'etc')
SMASHLIB_DIR = dirname(__file__)
USER_CONFIG_PATH = os.path.join(SMASH_DIR, fname_user_config)
ALIAS_CONFIG_PATH = os.path.join(DIR_SMASH_ETC, 'aliases.json')
MACRO_CONFIG_PATH = os.path.join(DIR_SMASH_ETC, 'macros.json')
EDITOR_CONFIG_PATH = os.path.join(DIR_SMASH_ETC, fname_editor_config)
ENV_CONFIG_PATH = os.path.join(DIR_SMASH_ETC, 'env.json')
PROMPT_CONFIG_PATH = os.path.join(DIR_SMASH_ETC, 'prompt.json')

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
