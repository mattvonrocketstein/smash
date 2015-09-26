""" smashlib.plugins.env_command
"""
import os
from smashlib import get_smash
from smashlib.plugins import Plugin
from smashlib.patches.base import PatchMagic
from smashlib.completion import smash_env_complete

env_completer = lambda himself, event: smash_env_complete(event.symbol)
env_regex = r'env [A-Za-z0-9_]+$'

class PatchEnv(PatchMagic):
    """
        Patches builtin "env" command to add support for wildcard queries.

        Example:

            smash$ env XTERM*


            { 'XTERM_LOCALE': 'en_US.UTF-8',
              'XTERM_SHELL': '/bin/bash',
              'XTERM_VERSION': 'XTerm(297)' }

    """

    name = 'env'

    def __call__(self, parameter_s=''):
        split = '=' if '=' in parameter_s else ' '
        bits = parameter_s.split(split)
        if len(bits) == 1 and bits[0]:
            varname = bits[0]
            if varname[-1].endswith('*'):
                return dict([[k, v] for k, v in os.environ.items()
                             if k.startswith(varname[:-1])])
        return self.original(parameter_s)


class EnvCommand(Plugin):

    verbose = True

    def init(self):
        self.contribute_patch(PatchEnv)
        self.contribute_completer(
            env_regex, env_completer)


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return EnvCommand(get_ipython()).install()
