""" smashlib.util

    Keep imports simple to avoid cycles!
    Safe, simple packages only (no ipython imports in here)
    Stick to stdlib, or known-safe sections of smashlib
"""
import os
import re
import glob

from goulash._os import home
from goulash._os import touch_file
from goulash.python import expanduser
from goulash.python import get_env
from goulash.python import opd
from goulash.python import ope
from goulash.python import opj
from goulash.python import ops
from smashlib.data import P_CODE_FILE

from report import Reporter as BaseReporter



class CLOpt(object):
    def __init__(self, args=None, kargs=None):
        assert args and kargs
        self.args = args
        self.kargs = kargs

class Reporter(BaseReporter):
    pass


def _guess_dir_type(_dir, max_depth=3):
    type_map = P_CODE_FILE.copy()
    type_map.update({
        'test*': 'tests',
    })
    # create a list based on max-depth like ['*', '*/*', '*/*/*', ..]
    globs = [os.path.sep.join(['*'] * x) for x in range(1, max_depth + 1)]
    matches = {}
    for ftype, ftype_name in type_map.items():
        for expr in globs:
            expr = expr + ftype
            if glob.glob(os.path.join(_dir, expr)):
                matches[ftype_name] = _dir
                break
    return matches


def guess_dir_type(_dir, **kargs):
    """ given a directory and a depth, find which types of
        files are in the directory.  this implementation
        should be reasonably efficient since it won't count
        the number of items or anything.
    """
    return _guess_dir_type(_dir, **kargs).keys()


def is_path(input):
    if len(input.split()) == 1 and \
       (os.path.exists(input) or
            input.startswith('./') or
            input.startswith('~/') or
            input.startswith('/')):
        return True


def split_on_unquoted_semicolons(txt):
    # use this in "ed fpath:1:2"?
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]
