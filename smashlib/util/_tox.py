""" smashlib.util._tox

    TODO: move to goulash
"""

import ConfigParser

from goulash.python import opj, ope


def has_tox(pdir):
    return ope(opj(pdir, 'tox.ini'))


def get_tox_envs(_dir=None):
    """ """
    ini_file = 'tox.ini' if _dir is None else opj(dir, 'tox.ini')
    if ope(ini_file):
        config = ConfigParser.ConfigParser()
        with open('tox.ini') as fhandle:
            config.readfp(fhandle)
        env_list = [x.split(':')[-1] for x in config.sections() if ':' in x]
        return env_list
