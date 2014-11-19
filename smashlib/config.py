""" smashlib.config
"""
import os, shutil

import demjson
from IPython.core.profiledir import ProfileDir

from smashlib.data import SMASH_ETC, SMASH_DIR, SMASHLIB_DIR, main_profile_name
from smashlib.python import create_dir_if_not_exists, ope, opj
from smashlib.data import USER_CONFIG_PATH

class SmashConfig(object):
    """
    """
    def __init__(self, config=None):
        self.config = config

    def load_from_etc(self, fname, schema=None):
        """ if schema is given, validate it.  otherwise just load blindly """
        with open(opj(SMASH_ETC, fname)) as fhandle:
            return demjson.decode(fhandle.read())

    @staticmethod
    def ensure_base_dir():
        create_dir_if_not_exists(SMASH_DIR)
        create_dir_if_not_exists(SMASH_ETC)
        return SMASH_DIR

    @staticmethod
    def ensure_profile():
        """ """
        canonical_prof = os.path.join(SMASHLIB_DIR, 'ipython_config.py')
        ProfileDir.create_profile_dir_by_name(SMASH_DIR, main_profile_name)
        profile_dir = os.path.join(SMASH_DIR, 'profile_'+main_profile_name)
        config_file = os.path.join(profile_dir, 'ipython_config.py')
        shutil.copy(canonical_prof, config_file,)
        return profile_dir

    @staticmethod
    def ensure():
        smash_dir = SmashConfig.ensure_base_dir()
        smash_prof = SmashConfig.ensure_profile()
        return dict(profile=smash_prof,dir=smash_dir)

class SmashUserConfig(object):
    @staticmethod
    def ensure():
        canonical_user_prof = os.path.join(
            SMASHLIB_DIR, 'user_config.py')
        if not ope(USER_CONFIG_PATH):
            shutil.copy(canonical_user_prof, USER_CONFIG_PATH)

    @staticmethod
    def load(env):
        from smashlib.data import USER_CONFIG_PATH
        print '..loading SmaSh user-config from:', USER_CONFIG_PATH
        sandbox = env.copy();
        sandbox.update(__file__=USER_CONFIG_PATH)
        execfile(USER_CONFIG_PATH, sandbox)
        return sandbox
