""" smash.python
"""

import os
import glob

opj = os.path.join
ops = os.path.split
glob = glob.glob

def only_py_files(dir, rel=False):
    result = glob(opj(dir, '*.py'))
    if rel: result = [ ops(fname)[-1] for fname in result]
    return result
