""" smash.python
"""

import os
import glob

opj = os.path.join
ope = os.path.exists
ops = os.path.split
opd = os.path.dirname
expanduser = os.path.expanduser

glob = glob.glob

def only_py_files(dir, rel=False):
    """ """
    result = glob(opj(dir, '*.py'))
    if rel: result = [ ops(fname)[-1] for fname in result]
    return result
