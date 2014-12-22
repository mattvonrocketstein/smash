""" smashlib.plugins.prefilter_url
"""
from smashlib.util.ipy import register_prefilter
from smashlib.prefilters.url import URLChecker, URLHandler
from smashlib.plugins import Plugin
from smashlib.util.ipy import uninstall_prefilter

class URLPlugin(Plugin):
    """ installs the IPython prefilter which handles urls """
    def install(self):
        register_prefilter(URLChecker, URLHandler)
        return self

    def uninstall(self):
        return uninstall_prefilter(URLChecker, URLHandler)

def load_ipython_extension(ip):
    """ called by %load_ext magic """
    return URLPlugin(get_ipython()).install()

def unload_ipython_extension(ip):
    """ called by %unload_ext magic """
    plugin = URLPlugin()
    plugin.uninstall()
