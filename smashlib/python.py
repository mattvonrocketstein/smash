""" smash.python
    TODO: probably move everything to util
"""

import os
import glob

opj        = os.path.join
ope        = os.path.exists
ops        = os.path.split
opd        = os.path.dirname
listdir    = os.listdir
isdir      = os.path.isdir
makedir    = mkdir = os.mkdir
dirname    = os.path.dirname
splitext   = os.path.splitext
abspath    = os.path.abspath
getcwd     = os.getcwd
glob       = glob.glob
get_env    = os.environ.get
expanduser = os.path.expanduser
splitext   = os.path.splitext

def create_dir_if_not_exists(apath):
    """ returns a bool for 'created'
    """
    if not ope(apath):
        os.mkdir(apath)
        return True
    return False

def only_py_files(dir, rel=False):
    """ """
    result = glob(opj(dir, '*.py'))
    if rel: result = [ ops(fname)[-1] for fname in result]
    return result
