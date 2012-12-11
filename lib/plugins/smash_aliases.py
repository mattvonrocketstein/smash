""" ipy_smash_aliases

    TODO: these aliases may not survive a "rehash" when proj is activated?
"""

from smashlib.smash_plugin import SmashPlugin
from IPython.Magic import Magic

def install_aliases():
    # avoid an unpleasant surprise:
    # patch reset to clean up the display like bash, not reset the namespace.
    def reset(himself, parameter_s=''):
        __IPYTHON__.system('reset')
        return 'overridden'
    Magic.magic_reset = reset

class Plugin(SmashPlugin):
    def install(self):
        install_aliases()
