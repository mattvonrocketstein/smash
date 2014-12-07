""" smashlib.plugins.cli_command_runner

    This plugin is responsible for doing the
    work whenever smash is invoked with "-c".
    Semantics are the same as "python -c" or
    "bash -c"
"""

from smashlib.util.events import receives_event
from smashlib.v2 import Reporter
from smashlib.channels import C_SMASH_INIT_COMPLETE, C_FILE_INPUT

class RunCommand(Reporter):
    verbose = True
    command = None

    def build_argparser(self):
        parser = super(RunCommand, self).build_argparser()
        parser.add_argument('-c','--command', default='')
        return parser

    def parse_argv(self):
        args, unknown = super(RunCommand, self).parse_argv()
        if args.command:
            self.command = args.command
        return args, unknown

    @receives_event(C_SMASH_INIT_COMPLETE)
    def run_command(self):
        if self.command is not None:
            self.smash.shell.run_cell(self.command)
            self.smash.shell.run_cell('exit')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = RunCommand(ip)
    tmp.install()
    return tmp

def unload_ipython_extension(ip):
    plugin_name = os.path.splitext(os.path.split(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
