""" apt_completers.py

    install IPython's completion for debian/ubuntu's apt.

    TODO: ipython's default is very slow

"""

from smashlib.smash_plugin import SmashPlugin
from IPython.Extensions.ipy_completers import apt_get_packages, apt_completer
from smashlib.util import set_complete, last_command_hook

@last_command_hook
def apt_hook(sys_cmd):
    if 'apt-get install' in sys_cmd:
        report.setup_py(
            'detected that you ran "apt-get install", '
            'rehasing env for new commands')
        __IPYTHON__.magic_rehashx()

class Plugin(SmashPlugin):
    def install(self):
        set_complete(apt_completer, 'apt-get')
        self.add_hook('generate_prompt', apt_hook, 0)
