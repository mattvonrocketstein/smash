""" smashlib.plugins.fabric
    documentation: http://mattvonrocketstein.github.io/smash/plugins.html#fabric
"""
import os
import inspect

from smashlib.v2 import Reporter
from smashlib.python import abspath, ope
from smashlib.completion  import opt_completer
from smashlib import get_smash

@opt_completer('fab')
def fabric_completer(self, event):
    """ """
    if ope('fabfile.py'):
        _fabfile = 'fabfile.py'
    elif ope('Fabfile.py'):
        _fabfile = 'Fabfile.py'
    exec 'import {0} as fabfile'.format(os.path.splitext(_fabfile)[0])
    out = []
    for x in inspect.getmembers(fabfile, inspect.isfunction):
        name,fxn=x
        if not x[0].startswith('_') and inspect.getfile(fxn)==abspath(_fabfile):
            out.append(name)
    return out

class FabricPlugin(Reporter):
    def install(self):
        self.smash.add_completer(fabric_completer, re_key='fab .*')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = FabricPlugin(ip)
    tmp.install()
    return tmp

def unload_ipython_extension(ip):
    get_smash()
