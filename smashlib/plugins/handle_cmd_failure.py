""" smashlib.plugins.handle_cmd_failure

    This plugin receives a signal whenever there
    is a failure executing a system command.
"""

from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_COMMAND_FAIL, C_FILE_INPUT
from smashlib.util import is_path


class HandleCommandFail(Plugin):
    verbose = True

    @receives_event(C_COMMAND_FAIL)
    def on_system_fail(self, cmd, error):
        if is_path(cmd):
            self.smash.publish(C_FILE_INPUT, cmd)


def load_ipython_extension(ip):
    return HandleCommandFail(get_ipython()).install()

from smashlib import get_smash
from goulash.python import splitext, ops


def unload_ipython_extension(ip):
    plugin_name = splitext(ops(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
