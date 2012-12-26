""" completion for debian/ubuntu's apt
"""

#This might be newer than what's in ipython
APT_CMDS = ("update upgrade install remove autoremove "
            "purge source build-dep dist-upgrade "
            "dselect-upgrade clean autoclean check "
            "changelog download").split()

from smashlib.util import set_complete
from smashlib.smash_plugin import SmashPlugin
from IPython.Extensions.ipy_completers import apt_get_packages, apt_completer

class Plugin(SmashPlugin):
    def install(self):
        set_complete(apt_completer, 'apt-get')
