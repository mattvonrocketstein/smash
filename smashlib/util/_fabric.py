""" smashlib.util.fabric

    TODO: move to goulash
"""

from fabric.api import lcd
from fabric.api import local
from fabric.api import quiet


class MissingSystemCommand(RuntimeError):
    pass


def qlocal(*args, **kargs):
    with quiet():
        return local(*args, **kargs)


def has_bin(name):
    result = qlocal('which "{0}"'.format(name))
    return result.succeeded


def require_bin(name, msg=None):
    if not has_bin(name):
        msg = msg or "{0} is required".format(name)
        raise MissingSystemCommand(msg)
