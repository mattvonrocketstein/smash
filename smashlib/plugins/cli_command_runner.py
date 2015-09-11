""" smashlib.plugins.cli_command_runner
"""

from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_SMASH_INIT_COMPLETE


class RunCommand(Plugin):
    """ This plugin is responsible for doing the work whenever smash
        is invoked with "-c". Semantics are the same as "python -c"
        or "bash -c"
    """
    verbose = True
    command = None

    def get_cli_arguments(self):
        return [
            [['-c', '--command'], dict(default='')]
        ]

    def use_argv(self, args):
        if args.command:
            self.command = args.command

    @receives_event(C_SMASH_INIT_COMPLETE)
    def run_command(self):
        if self.command is not None:
            self.smash.shell.run_cell(self.command)
            self.smash.shell.run_cell('exit')


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = RunCommand(ip).install()
    return tmp

from smashlib import get_smash
from goulash.python import splitext, ops


def unload_ipython_extension(ip):
    plugin_name = splitext(ops(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
