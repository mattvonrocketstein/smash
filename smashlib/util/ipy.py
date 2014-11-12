""" smashlib.util.ipy

    import shortcuts for ipython.  this also might help to keep
    smashlib in sync with changing ipython target versions?
"""
import os, shutil
from smashlib.data import SMASH_DIR, SMASHLIB_DIR, main_profile_name
from smashlib.python import ope
from IPython.core.profiledir import ProfileDir
from IPython.utils.coloransi import TermColors
from smashlib.data import user_config_name, USER_CONFIG_PATH

def green(txt):
    return TermColors.Green + txt + TermColors.Normal

class SmashConfig(object):
    @staticmethod
    def ensure_base_dir():
        if not ope(SMASH_DIR):
            os.mkdir(SMASH_DIR)
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
        return smash_prof

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
