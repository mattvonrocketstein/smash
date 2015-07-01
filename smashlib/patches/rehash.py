""" smashlib.patches.rehash
"""
from smashlib import get_smash
from smashlib.patches.base import PatchMagic
from smashlib.channels import C_REHASH_EVENT


class PatchRehash(PatchMagic):

    """ patches the builtin ipython rehashx so that a post-rehash
        event can be sent to anyone who wants to subscribe
    """

    name = 'rehashx'

    def __call__(self, parameter_s=''):
        self.original(parameter_s)
        get_smash().publish(C_REHASH_EVENT)
