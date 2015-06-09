#!/usr/bin/env python
#

import os,sys
import imp
import logging
from smashlib.util import require_ipy
#from smashlib.util.reflect import namedAny
import importlib
class RewriteIPythonImport(object):
    def __init__(self):
        pass

    def find_module(self, fullname, path=None):
        print fullname, path
        if fullname.startswith('IPython'):
            new_fullname = ['smashlib','ipy3x']+fullname.split('.')[1:]
            new_fullname='.'.join(new_fullname)
            logging.warning("rewriting IPython import: {0}->{1}".format(fullname, new_fullname))
            self.path = path
            self.original_name = fullname
            self.rewritten_name = new_fullname
            return self
        return None

    def load_module(self, name):
        result = importlib.import_module(self.rewritten_name)
        sys.modules[name] = result
        return result

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
