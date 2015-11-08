""" smashlib.patches.base
"""
from smashlib import get_smash
class Patch(object):
    pass

class PatchMagic(Patch):

    """ helper for patching ipython builtin line magics.
        it has to be done this way because ipy.shell.magics_manager
        is no help: the register_function() call can only change
        magics_manager.user_magics
    """
    name = None
    patched = False

    def __init__(self, *args):
        self.smash = get_smash()
        self.shell = self.smash.shell
        self.original = self.shell.magics_manager.magics['line'][self.name]
        self.patched = True

    def install(self):
        self.shell.magics_manager.magics['line'][self.name] = self
