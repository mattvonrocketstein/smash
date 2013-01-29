""" apt_completers.py

    install IPython's completion for debian/ubuntu's apt.

    TODO: ipython's default is very slow

"""

from smashlib.util import set_complete
from smashlib.smash_plugin import SmashPlugin
from IPython.Extensions.ipy_completers import apt_get_packages, apt_completer

class Plugin(SmashPlugin):
    def install(self):
        set_complete(apt_completer, 'apt-get')
