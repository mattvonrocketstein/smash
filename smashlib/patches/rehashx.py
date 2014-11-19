""" smashlib.patches.rehashx

    TODO: wait actually this is dumb.  send a "refresh"
          event and have a subscriber that runs rehashx
"""
import os

from smashlib.patches.base import PatchMagic
from smashlib.channels import C_REHASH_EVENT


class PatchRehashX(PatchMagic):
    """ patches the builtin ipython rehashx magic so that a post-dir-change
        event can be sent to anyone who wants to subscribe, and so that
        the "rehashx" command is quiet by default.
    """

    name = 'rehashx'

    def __call__(self, parameter_s=''):
        self.original(parameter_s)
        from smashlib.util import get_smash
        get_smash().publish(C_REHASH_EVENT,
                            None)
