""" simple completion for debian/ubuntu's apt

    want to trigger on:
"""

APT_CMDS = ("update upgrade install remove autoremove "
            "purge source build-dep dist-upgrade "
            "dselect-upgrade clean autoclean check "
            "changelog download").split()

from smashlib.util import set_complete
from smashlib.plugins import SmashPlugin

class Plugin(SmashPlugin):
    def install(self):
        completer = lambda *args,**kargs: APT_GET_CMDS
        set_complete(completer, 'apt-get')
