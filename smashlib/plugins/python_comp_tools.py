""" smashlib.plugins.python_comp_tools
    This code adds tab completion over tox CLI options,
    and dynamic determination of environments for "tox -e"
"""
import os
from smashlib import get_smash
from smashlib.v2 import Reporter
from smashlib.util._tox import get_tox_envs
from smashlib.completion  import opt_completer

#@opt_completer('python setup.py')
def setup_completer(self,event):
    return 'install develop build'.split()

@opt_completer('tox')
def tox_completer(self, event):
    return []

def tox_env_completer(self, event):
    line = event.line
    if line and line.split()[-1].strip().endswith('-e'):
        return get_tox_envs()

class ToxPlugin(Reporter):
    def install(self):
        self.smash.add_completer(tox_env_completer, re_key='tox .*-e')
        self.smash.add_completer(tox_completer, re_key='tox .*')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = ToxPlugin(ip)
    tmp.install()
    return tmp

def unload_ipython_extension(ip):
    plugin_name = os.path.splitext(os.path.split(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
