""" smashlib.plugins.cli_update
"""

from fabric import api
from goulash.python import splitext, ops

from smashlib import get_smash
from smashlib.util import CLOpt
from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_SMASH_INIT_COMPLETE
from smashlib import data

from gittle import Gittle
class UpdateSmash(Plugin):
    """ This plugin is responsible for doing the work whenever smash
        is invoked with "--update".
    """
    update = None
    verbose = True # do not change

    def get_cli_arguments(self):
        update_clopt = CLOpt(
            args = ['--update'],
            kargs=dict(default=False,
                       action='store_true'))
        return [update_clopt]

    def use_argv(self, args):
        if args.update:
            self.update = True

    @receives_event(C_SMASH_INIT_COMPLETE)
    def consider_updating(self):
        if self.update is not None:
            try:
                self.run_update()
            finally:
                self.smash.shell.run_cell('exit')

    def run_update(self):
        smash_dir = data.SMASH_DIR)
        with api.lcd(smash_dir):
            with api.settings(api.hide('warnings'), warn_only=True, quiet=True):
                result = api.local('git diff-index --quiet HEAD --')
            changed = (1 == result.return_code)
            if changed:
                error = "aborting due to local changes in {0}"
                self.report(error.format(smash_dir))
            else:
                api.local('git pull')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return UpdateSmash(get_ipython()).install()
