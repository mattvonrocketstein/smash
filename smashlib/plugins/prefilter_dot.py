""" smashlib.plugins.prefilter_dot
"""
from smashlib.util.ipy import register_prefilter
from smashlib.prefilters.dot import DotChecker, DotHandler
from smashlib.v2 import SmashComponent
from smashlib.util.ipy import uninstall_prefilter

class DotPlugin(SmashComponent):
    """ installs the IPython prefilter which handles dot-commands. """
    def install(self):
        return register_prefilter(DotChecker, DotHandler)
    def uninstall(self):
        return uninstall_prefilter(DotChecker, DotHandler)

def load_ipython_extension(ip):
    """ called by %load_ext magic """
    plugin = DotPlugin()
    plugin.install()
    return plugin


def unload_ipython_extension(ip):
    """ called by %unload_ext magic """
    plugin = DotPlugin()
    plugin.uninstall()
