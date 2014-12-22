""" smashlib.plugins.fabric
    documentation: http://mattvonrocketstein.github.io/smash/plugins.html#fabric
"""
import os
import inspect

from smashlib.plugins import Plugin
from goulash.python import ope
from smashlib.completion  import opt_completer
from smashlib import get_smash

@opt_completer('fab')
def fabric_completer(self, event):
    """ """
    out = []
    if ope('fabfile.py'):
        _fabfile = 'fabfile.py'
    elif ope('Fabfile.py'):
        _fabfile = 'Fabfile.py'
    else:
        return out

    try:
        exec 'import {0} as fabfile'.format(os.path.splitext(_fabfile)[0])
    except Exception,e:
        print 'error importing fabfile'+str(e)
    for (name,fxn) in inspect.getmembers(fabfile, inspect.isfunction): # NOQA
        if not name.startswith('_') and getattr(fxn, '__module__',None)=='fabfile':
            out.append(name)
    return out

class FabricPlugin(Plugin):
    def install(self):
        self.smash.add_completer(fabric_completer, re_key='fab .*')
        return self

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return FabricPlugin(get_ipython()).install()

def unload_ipython_extension(ip):
    get_smash()
