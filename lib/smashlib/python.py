""" smash.python
    TODO: probably move everything to util
"""

import os
import glob

makedir = mkdir = os.mkdir
opj = os.path.join
ope = os.path.exists
ops = os.path.split
opd = os.path.dirname
splitext   = os.path.splitext
abspath    = os.path.abspath
expanduser = os.path.expanduser
getcwd     = os.getcwd
glob       = glob.glob

def only_py_files(dir, rel=False):
    """ """
    result = glob(opj(dir, '*.py'))
    if rel: result = [ ops(fname)[-1] for fname in result]
    return result
