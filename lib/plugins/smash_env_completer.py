""" smash_env_completer

    Completes stuff along the lines of "echo $VIRTUAL_EN<tab>"
"""
import os
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report, set_complete

def env_completer(self, event):
    return os.environ.keys()

class Plugin(SmashPlugin):
    def install(self):
        set_complete(env_completer, '.* \$.*', priority=100)
