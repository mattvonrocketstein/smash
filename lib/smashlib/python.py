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
splitext   = os.path.splitext
abspath    = os.path.abspath
getcwd     = os.getcwd
glob       = glob.glob
get_env    = os.environ.get
expanduser = os.path.expanduser

def only_py_files(dir, rel=False):
    """ """
    result = glob(opj(dir, '*.py'))
    if rel: result = [ ops(fname)[-1] for fname in result]
    return result
