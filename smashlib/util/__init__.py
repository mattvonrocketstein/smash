""" smashlib.util

    Keep imports simple to avoid cycles!
    Safe, simple packages only (no ipython imports in here)
    Stick to stdlib, or known-safe sections of smashlib
"""
import os, re
from smashlib.python import get_env, opd, ops, opj, ope, expanduser
from smashlib.util.reflect import from_dotpath

def home():
    return get_env('HOME')

def require_ipy(require_version):
    import IPython
    ipy_version = IPython.__version__
    if not ipy_version.startswith(require_version):
        err = "smash requires ipython {0}, but your version is {1}"
        raise SystemExit(err.format(require_version, ipy_version))

def get_smash():
    ip = get_ipython()
    try:
        return ip._smash
    except AttributeError:
        raise Exception("load smash first")


import glob, os
def guess_dir_type(_dir, max_depth=3):
    """ given a directory and a depth, find which types of
        files are in the directory.  this implementation
        should be reasonably efficient since it won't count
        the number of items or anything.
    """
    type_map = {
        '.py':'python',
        '.pp':'puppet',
        '.md':'docs',
        'Vagrantfile':'vagrant',
        }
    # create a list based on max-depth like ['*', '*/*', '*/*/*', ..]
    globs = [os.path.sep.join(['*']*x) for x in range(1,max_depth+1)]
    matches = []
    for ftype, ftype_name in type_map.items():
        for expr in globs:
            expr = expr + ftype
            if glob.glob(os.path.join(_dir,expr)):
                matches.append(ftype_name)
                break
    return matches

def report(msg, *args, **kargs):
    from .ipy import TermColors
    context_name = kargs.pop('context_name','no-context')
    print "{0}: {1} {2}".format(
        TermColors.Blue + context_name,
        TermColors.Red + msg,
        TermColors.Normal
        )
    if args:
        print '  ',args

def split_on_unquoted_semicolons(txt):
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]
