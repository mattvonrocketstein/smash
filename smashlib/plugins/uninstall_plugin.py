""" smashlib.plugins.uninstall_plugin
"""
from smashlib import get_smash
from smashlib.plugins import Plugin

class UninstallPlugins(Plugin):
    def install(self):
        def fxn(*args):
            return get_smash()._installed_plugins.keys()
        self.contribute_completer('uninstall_plugin .*', fxn)
        self.contribute_completer('%uninstall_plugin .*', fxn)
        return self

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    return UninstallPlugins(get_ipython()).install()

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    get_smash()._installed_plugins['liquidprompt'].uninstall()
