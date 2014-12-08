""" smashlib.patches.cd
"""
import os

from smashlib.patches.base import PatchMagic
from smashlib.channels import C_CHANGE_DIR


class PatchCDMagic(PatchMagic):
    """ patches the builtin ipython cd magic so that a post-dir-change
        event can be sent to anyone who wants to subscribe, and so that
        the "cd" command is quiet by default.
    """

    name = 'cd'

    def __call__(self, parameter_s=''):
        try:
            self.original('-q '+parameter_s)
        except Exception:
            self.component.report("error with cd.")
            raise
        else:
            this_dir = self.smash.system('pwd', quiet=True)
            self.smash.bus.publish(
                C_CHANGE_DIR, this_dir,
                self.component.last_dir)
            os.environ['PWD'] = this_dir
            self.component.last_dir = this_dir
