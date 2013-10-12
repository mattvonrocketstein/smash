""" pip_completer.py

    Provides completion for the standard pip subcommands.
    Also, "pip install <tab>" will be made to complete
    values from requirements.txt whenever such a file
    exists in the working directory.

    TODO: rename to smash_pip

"""
import os

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report, set_complete, last_command_hook

PIP_CMDS = 'bundle freeze help install search uninstall unzip zip'.split()

def pip_complete(self, event):
    return PIP_CMDS

@last_command_hook
def pip_hook(sys_cmd):
    # FIXME: probably just use setup_re
    if sys_cmd.startswith('pip'):
        report.setup_py("detected that you ran pip.. "
                        "rehashing env")
        __IPYTHON__.magic_rehashx()

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
        self.add_hook('generate_prompt', pip_hook, 0)
