""" smashlib.plugins.uninstall_plugin
"""
from smashlib import get_smash
from smashlib.plugins import Plugin

# FIXME: deprecate?
class UninstallPlugins(Plugin):

    def install(self):
        def plugin_name_completer(*args):
            tmp = get_smash()._installed_plugins.keys()
            print tmp
        self.contribute_completer('uninstall_plugin .*', plugin_name_completer)
        self.contribute_completer('%uninstall_plugin .*', plugin_name_completer)
        return self


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    return UninstallPlugins(get_ipython()).install()


def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    get_smash()._installed_plugins['uninstallplugin'].uninstall()
