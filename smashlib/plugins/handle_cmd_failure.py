""" smashlib.plugins.handle_cmd_failure

    This plugin receives a signal whenever there
    is a failure executing a system command.
"""

from smashlib.v2 import Reporter
from smashlib.util.events import receives_event
from smashlib.channels import C_FAIL, C_FILE_INPUT
from smashlib.util import is_path

class HandleCommandFail(Reporter):
    verbose = True

    @receives_event(C_FAIL)
    def on_system_fail(self, cmd, error):
        if is_path(cmd):
            self.smash.publish(C_FILE_INPUT, cmd)


def load_ipython_extension(ip):
    ip = get_ipython()
    tmp = HandleCommandFail(ip)
    tmp.install()
    return tmp

from smashlib import get_smash
from goulash.python import splitext,ops
def unload_ipython_extension(ip):
    plugin_name = splitext(ops(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
