""" smashlib.plugins.cli_command_runner
"""

from fabric.api import lcd

from goulash.python import opj
from goulash._fabric import qlocal
from smashlib.plugins import Plugin
from smashlib.data import SMASH_DIR
from smashlib.util.events import receives_event
from smashlib.channels import C_SMASH_INIT_COMPLETE

bootstrap_file = 'bootstrap.sh'

class UpdateCommand(Plugin):
    """ This plugin is responsible for doing the
        work whenever smash is invoked with "-u".
        Semantics are
    """

    verbose = True
    update = False

    def build_argparser(self):
        parser = super(UpdateCommand, self).build_argparser()
        parser.add_argument('-u', '--update', default=False, action='store_true')
        return parser

    def parse_argv(self):
        args, unknown = super(UpdateCommand, self).parse_argv()
        if args.update:
            self.update = args.update
        return args, unknown

    @receives_event(C_SMASH_INIT_COMPLETE)
    def maybe_update(self):
        """ if --update was given on the command
            line, update whenever init is complete """
        if self.update:
            self._update()

    def _reinstall(self):
        print self.smash.system(opj(SMASH_DIR, 'bin', "python") + " setup.py develop")

    def _update(self):
        cmd = opj(SMASH_DIR, bootstrap_file)
        with lcd(SMASH_DIR):
            head = self.smash.system("git rev-parse HEAD")
            branch = self.smash.system("git branch|grep '\*'")
            branch = branch.strip().split()[-1]
            fetch_result = self.smash.system("git fetch")
            new_head = self.smash.system("git rev-parse HEAD")
            changed = new_head != head
            if changed:
                self.report(("smash branch {0} has changed {1} {2}").format(
                    branch, head, new_head))
                self._reinstall()
            else:
                self.report(('smash is already updated for '
                             'the current branch ({0})').format(branch))
        self.die('{0} {1}'.format(cmd, [branch, head, changed]))
        self.die('update finished')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = UpdateCommand(ip).install()
    return tmp

from smashlib import get_smash
from goulash.python import splitext, ops

def unload_ipython_extension(ip):
    plugin_name = splitext(ops(__file__)[-1])[0]
    get_smash().plugins[plugin_name].uninstall()
