""" smashlib.plugins.cd_hooks

"""
import os
from smashlib import get_smash
from smashlib.plugins import Plugin
from smashlib.patches.base import PatchMagic
from smashlib.completion import smash_env_complete





class PatchEnv(PatchMagic):

    """ patches the builtin ipython rehashx so that a post-rehash
        event can be sent to anyone who wants to subscribe
    """

    name = 'env'

    def __call__(self, parameter_s=''):
        """List environment variables."""
        split = '=' if '=' in parameter_s else ' '
        bits = parameter_s.split(split)
        # support for wildcard quality
        if len(bits) == 1 and bits[0]:
            varname = bits[0]
            if varname[-1].endswith('*'):
                return dict([[k, v] for k, v in os.environ.items()
                             if k.startswith(varname[:-1])])

        return self.original(parameter_s)


def env_completer(self, event):
    symbol = event.get('symbol','').strip()
    if not symbol:
        return
    return [k for k in os.environ
            if k.startswith(symbol)]


class EnvCommand(Plugin):
    verbose = True

    def init(self):
        PatchEnv(get_smash()).install()
        self.smash.add_completer(
            env_completer, #smash_env_complete,
            re_key=r'env [A-Za-z0-9_]+$')


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return EnvCommand(get_ipython()).install()
