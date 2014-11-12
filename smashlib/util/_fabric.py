""" smashlib.util.fabric
"""

from fabric.api import quiet, local

def qlocal(*args, **kargs):
    with quiet():
        return local(*args, **kargs)

def has_bin(name):
    result =  qlocal('which "{0}"'.format(name))
    return result.succeeded

def require_bin(name, msg=None):
    if not has_bin(name):
        msg = msg or "{0} is required".format(name)
        raise Exception(msg)
