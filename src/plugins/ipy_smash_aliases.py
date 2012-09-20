""" ipy_smash_aliases

    general shell aliases.  this stuff is somewhat idiosyncratic
    to my own needs, but it's kind of just a place to throw your
    old bash aliases so transitioning to smash isn't too painful

    TODO: these aliases may not survive a "rehash" when proj is activated?
"""

def install_aliases():
    # FIXME: can't move the import?  plus this is in the wrong file
    from IPython.Magic import Magic
    # avoid an unpleasant surprise:
    # patch reset to clean up the display like bash, not reset the namespace.
    def reset(himself, parameter_s=''):
        __IPYTHON__.system('reset')
        return 'overridden'
    Magic.magic_reset = reset

from smash.plugins import SmashPlugin
class Plugin(SmashPlugin):
    def install(self):
        install_aliases()
