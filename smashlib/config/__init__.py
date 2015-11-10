""" smashlib.config
"""
import os
import shutil
import demjson
import voluptuous

from IPython.core.profiledir import ProfileDir

from goulash.python import (
    create_dir_if_not_exists, ope, opj)

from smashlib.data import (
    DIR_SMASH_ETC, SMASH_DIR,
    SMASHLIB_DIR, main_profile_name)

from smashlib.util import Reporter
from smashlib.config import schemas
from smashlib._logging import smash_log
from smashlib.data import USER_CONFIG_PATH
from smashlib.exceptions import ConfigError

report = Reporter("SmashConfig")


def _find_schema(fname):
    fname = os.path.split(fname)[-1]
    fname = os.path.splitext(fname)[0]
    return getattr(schemas, fname)


class SmashConfig(object):

    """
    """

    def __init__(self, config=None):
        self.config = config

    def load_from_etc(self, fname, schema=None):
        """ if schema is given, validate it.  otherwise
            just load blindly """
        smash_log.info('loading and validating {0}'.format(fname))
        schema = schema or _find_schema(fname)
        absf = opj(DIR_SMASH_ETC, fname)
        try:
            with open(absf) as fhandle:
                data = demjson.decode(fhandle.read())
        except demjson.JSONDecodeError:
            err = "file is not json: {0}".format(absf)
            # boot_log.critical(err)
            raise ConfigError(err)
        except IOError:
            smash_log.info("{0} does not exist..".format(absf))
            if getattr(schema, 'default', None) is not None:
                smash_log.info("..but a default is defined.  writing file")
                default = schema.default
                if not isinstance(default, basestring):
                    default = demjson.encode(schema.default)

                with open(absf, 'w') as fhandle:
                    fhandle.write(default)
                return self.load_from_etc(fname, schema)
            else:
                err = ("{0} does not exist, and no default"
                       " is defined").format(absf)
                # boot_log.critical(err)
                self.log.critical(err)
                raise SystemExit(err)
        try:
            schema(data)
        except voluptuous.Invalid, e:
            raise SystemExit("error validating {0}\n\t{1}".format(absf, e))
        return data

    def update_from_etc(self, config, fname, schema=None):
        data = self.load_from_etc(fname, schema=schema)
        config.update(data)
        return data

    def append_from_etc(self, config, fname, schema=None):
        data = self.load_from_etc(fname, schema=schema)
        [config.append(x) for x in data]
        return data

    @staticmethod
    def ensure_base_dir():
        create_dir_if_not_exists(SMASH_DIR)
        create_dir_if_not_exists(DIR_SMASH_ETC)
        return SMASH_DIR

    @staticmethod
    def ensure_profile():
        """ """
        canonical_prof = os.path.join(SMASHLIB_DIR, 'ipython_config.py')
        ProfileDir.create_profile_dir_by_name(SMASH_DIR, main_profile_name)
        profile_dir = os.path.join(SMASH_DIR, 'profile_' + main_profile_name)
        config_file = os.path.join(profile_dir, 'ipython_config.py')
        shutil.copy(canonical_prof, config_file,)
        return profile_dir

    @staticmethod
    def ensure():
        smash_dir = SmashConfig.ensure_base_dir()
        smash_prof = SmashConfig.ensure_profile()
        return dict(profile=smash_prof, dir=smash_dir)


class SmashUserConfig(object):

    @staticmethod
    def ensure():
        canonical_user_prof = os.path.join(
            SMASHLIB_DIR, 'user_config.py')
        if not ope(USER_CONFIG_PATH):
            shutil.copy(canonical_user_prof, USER_CONFIG_PATH)

    @staticmethod
    def load(env):
        msg = '..loading SmaSh user-config from: {0}'
        msg = msg.format(USER_CONFIG_PATH)
        smash_log.debug(msg)
        sandbox = env.copy()
        sandbox.update(__file__=USER_CONFIG_PATH)
        execfile(USER_CONFIG_PATH, sandbox)
        return sandbox
