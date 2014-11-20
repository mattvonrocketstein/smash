""" smashlib.ipy_fabric
"""
import os
import inspect

from smashlib.python import ope,abspath
from smashlib.v2 import Reporter

def fabric_completer(self, event):
    line = event.line
    if line[-1]='-':
        return ['complete_options']
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
        self.smash.add_completer(fabric_completer, str_key='fab ')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = FabricPlugin(ip)
    tmp.install()
    return tmp

def unload_ipython_extension(ip):
    smash = get_smash()
    # not implemented
