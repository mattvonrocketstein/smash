#!/usr/bin/env python
#

import os,sys
import imp
import logging
from smashlib.util import require_ipy

class RewriteIPythonImport(object):
    def __init__(self):
        self.module_names = ['IPython']

    def find_module(self, fullname, path=None):
        print fullname,path
        if fullname in self.module_names:
            logging.warning("rewriting IPython import: %s", fullname, path)
            self.path = path
            return self
        return None

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]
        from smashlib import ipy3x
        sys.modules[name] = ipy3x
        return ipy3x

def my_import(name):
    try:
        m = __import__(name)
        for n in name.split(".")[1:]:
            m = getattr(m, n)
    except ImportError:
        raise ImportError("No such module: "+name)
    #except AttributeError:
    #    raise ImportError('No such module "{0}" in {1}'.format(n,m))
    return m
sys.meta_path = [RewriteIPythonImport()]
from IPython.terminal.interactiveshell import get_default_editor

def main():
    #REQUIRE_VERSION = '3.2.0-dev'
    #require_ipy(REQUIRE_VERSION)
    os.environ['SMASH'] = '1'
    from smashlib import embed
    from smashlib.config import SmashConfig, SmashUserConfig
    smash_prof = SmashConfig.ensure()['profile']
    SmashUserConfig.ensure()
    embed(["--profile-dir={0}".format(smash_prof),],
          # do not let smash inspect the caller context
          # and automatically update globals/locals
          user_ns=None
          )

entry = main

if __name__=='__main__':
    main()
