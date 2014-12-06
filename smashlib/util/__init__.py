""" smashlib.util

    Keep imports simple to avoid cycles!
    Safe, simple packages only (no ipython imports in here)
    Stick to stdlib, or known-safe sections of smashlib
"""
import os, re, glob

from goulash.python import get_env, opd, ops, opj, ope, expanduser


def home():
    return get_env('HOME')

def touch_file(_file):
    """ TODO: move to goulash """
    with open(_file, 'w') as handle:
        pass

def require_ipy(require_version):
    import IPython
    ipy_version = IPython.__version__
    if not ipy_version.startswith(require_version):
        err = "smash requires ipython {0}, but your version is {1}"
        raise SystemExit(err.format(require_version, ipy_version))

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

def is_path(input):
    if len(input.split())==1 and \
       (input.startswith('./') or \
        input.startswith('~/') or \
        input.startswith('/')):
        return True

def split_on_unquoted_semicolons(txt):
    # use this in "ed fpath:1:2"?
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]
