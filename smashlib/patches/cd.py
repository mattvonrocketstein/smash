""" smashlib.patches.cd
"""
import os

from smashlib.patches.base import PatchMagic
from smashlib.channels import C_CHANGE_DIR

# FIXME: move this to the "plugins.cd_hooks" ?


class PatchCDMagic(PatchMagic):

    """ patches the builtin ipython cd magic so that a post-dir-change
        event can be sent to anyone who wants to subscribe, and so that
        the "cd" command is quiet by default.
    """

    name = 'cd'
    last_dir = None

    def __call__(self, parameter_s=''):
        self.original('-q ' + parameter_s)
        this_dir = self.smash.system('pwd', quiet=True)
        self.smash.bus.publish(
            C_CHANGE_DIR, this_dir,
            self.last_dir)
        os.environ['PWD'] = this_dir
        self.last_dir = this_dir
