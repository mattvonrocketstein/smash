""" smashlib.import_hooks
"""

import imp
import os, sys
import logging
import importlib

class RewriteIPythonImport(object):
    def find_module(self, fullname, path=None):
        if fullname.startswith('IPython'):
            new_fullname = ['smashlib','ipy3x']+fullname.split('.')[1:]
            new_fullname='.'.join(new_fullname)
            #logging.warning("import : {0}->{1}".format(fullname, new_fullname))
            self.path = path
            self.original_name = fullname
            self.rewritten_name = new_fullname
            return self
        return None

    def load_module(self, name):
        result = importlib.import_module(self.rewritten_name)
        sys.modules[name] = result
        return result

def hijack_ipython_module():
    found = False
    for x in sys.meta_path:
        if isinstance(x, RewriteIPythonImport):
            found = True
            break
    if not found:
        sys.meta_path.append(RewriteIPythonImport())
