""" smashlib.plugins.prefilter_dot
"""
from smashlib.util.ipy import register_prefilter
from smashlib.prefilters.dot import DotChecker, DotHandler
from smashlib.plugins import Plugin
from smashlib.util.ipy import uninstall_prefilter

class DotPlugin(Plugin):
    """ installs the IPython prefilter which handles dot-commands. """
    def install(self):
        register_prefilter(DotChecker, DotHandler)
        return self

    def uninstall(self):
        return uninstall_prefilter(DotChecker, DotHandler)

def load_ipython_extension(ip):
    """ called by %load_ext magic """
    return DotPlugin(get_ipython()).install()


def unload_ipython_extension(ip):
    """ called by %unload_ext magic """
    plugin = DotPlugin()
    plugin.uninstall()
