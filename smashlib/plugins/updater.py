""" smashlib.plugins.updater
"""

from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_SMASH_INIT_COMPLETE
from smashlib.util._fabric import qlocal, lcd

class Updater(Plugin):
    """ This plugin is responsible for doing the
        work whenever smash is invoked with "-U"
        or "--update".
    """

    verbose = True
    command = None
    cli_update = False

    def build_argparser(self):
        parser = super(Updater, self).build_argparser()
        parser.add_argument('-U','--update',
                            default=False, action='store_true')
        return parser

    def parse_argv(self):
        args, unknown = super(Updater, self).parse_argv()
        if args.update:
            self.cli_update = True
        return args, unknown
    def run(self,cmd):
        self.report("running: ",cmd)
        return self.smash.system(cmd)
    def update(self):
        self.report("checking for a newer version")
        smash_repo = 'git://github.com/mattvonrocketstein/smash.git'
        with lcd("~/.smash"):
            cmd1 = 'git rev-parse HEAD'
            cmd2_t = 'git ls-remote {0} HEAD'
            r1 = self(cmd1, capture=True).strip()
            r2 = qlocal(cmd2_t.format(smash_repo), capture=True)
            r2 = r2.strip().split()[0]
            self.smash.shell.run_cell('which smashlib')
            self.report('local smash hash:    '+r1)
            self.report('upstream smash hash: '+r2)
            if r1!=r2:
                self.report('updating..')
                self.smash.system('git fetch')
                from goulash.python import opj
                from smashlib.data import SMASH_DIR
                pip = opj(SMASH_DIR,'bin','pip')
                self.run(
                    '{0} install -r install_requirements'.format(pip))
                self.run(
                    '{0} install -r requirements'.format(pip))
            else:
                self.report("versions match.. nothing to do")

    @receives_event(C_SMASH_INIT_COMPLETE)
    def maybe_update(self):
        if self.cli_update:
            self.update()
            self.smash.shell.run_cell('exit')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = Updater(ip).install()
    return tmp

from smashlib import get_smash
from goulash.python import splitext, ops
def unload_ipython_extension(ip):
    plugin_name = splitext(ops(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
