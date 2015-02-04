""" _django

"""

#import os
from IPython.core.magic import Magics, magics_class

from smashlib import get_smash
from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_CHANGE_DIR


@magics_class
class DjangoMagics(Magics):
    """ django magics for smash """

   # @line_magic
   # def j(self, parameter_s=''):
   #     tmp = parameter_s.split()
   #     if not tmp:
   #         return
   #     if not tmp[0].startswith('-'):
   #         result = autojump(tmp)
   #         get_ipython().magic('pushd '+result)
   #     else:
   #         try:
   #             return autojump(tmp)
   #         except SystemExit:
   #             pass

class DjangoPlugin(Plugin):

    def init_magics(self):
        self.shell.register_magics(DjangoMagics)

    @receives_event(C_CHANGE_DIR)
    def is_django(self, new_dir, old_dir):
        """ useful as a post-hook for "cd" commands. it might be
            a good idea to call this after the "jump" command or
            after "pushd" as well, but that's not implemented.
        """
        print 'checking if this is a django project'

    #def install(self):
    #    return self

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    return DjangoPlugin(ip).install()

def unload_ipython_extension(ip):
    get_smash()
    # not implemented
