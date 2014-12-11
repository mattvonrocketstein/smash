""" smashlib.plugins.prefilter_url
"""
from smashlib.util.ipy import register_prefilter
from smashlib.prefilters.url import URLChecker, URLHandler
from smashlib.v2 import SmashComponent
from smashlib.util.ipy import uninstall_prefilter

class URLPlugin(SmashComponent):
    """ installs the IPython prefilter which handles urls """
    def install(self):
        return register_prefilter(URLChecker, URLHandler)
    def uninstall(self):
        return uninstall_prefilter(URLChecker, URLHandler)

def load_ipython_extension(ip):
    """ called by %load_ext magic """
    plugin = URLPlugin()
    plugin.install()
    return plugin


def unload_ipython_extension(ip):
    """ called by %unload_ext magic """
    plugin = URLPlugin()
    plugin.uninstall()
