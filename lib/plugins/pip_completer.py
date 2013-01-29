""" pip_completer.py

    Provides completion for the standard pip subcommands.
    Also, "pip install <tab>" will be made to complete
    values from requirements.txt whenever such a file
    exists in the working directory.

"""
import os

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report, set_complete

PIP_CMDS = 'bundle freeze help install search uninstall unzip zip'.split()

def pip_complete(self, event):
    return PIP_CMDS

def requirements_complete(self, event):
    """ TODO: even smarter.. check $event and maybe use filesystem completer """
    if 'requirements.txt' in os.listdir(os.getcwd()):
        reqs = [x.strip() for x in open('requirements.txt').readlines() ]
        reqs = [x for x in reqs if not x.startswith('#')]
        return reqs
    return []


class Plugin(SmashPlugin):
    def install(self):
        set_complete(pip_complete, 'pip')
        set_complete(requirements_complete, 'pip install')
