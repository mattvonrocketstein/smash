""" smashlib.patches.pushd
"""
import os

from IPython.utils.path import unquote_filename
from IPython.utils import py3compat

from smashlib.patches.base import PatchMagic


class PatchPushdMagic(PatchMagic):

    name = 'pushd'

    def __init__(self, mycd):
        super(PatchPushdMagic, self).__init__()
        self.mycd = mycd

    def __call__(self, parameter_s=''):
        """ verbatim from core.magic.osm.pushd, except it calls mycd
            instead.  without this patch, function is noisy because
            it is using the ipython cd function and "-q" is
            not appended to parameter_s
        """
        dir_s = self.shell.dir_stack
        tgt = os.path.expanduser(unquote_filename(parameter_s))
        cwd = py3compat.getcwd().replace(
            self.shell.home_dir, '~')
        if tgt:
            self.mycd(parameter_s)
        dir_s.insert(0, cwd)
        return self.shell.magic('dirs')
