""" smash_autojump

    Adds the magic 'j' or 'jump' command, which tracks and weights every time
    you change directory.

    Basically 'j some_specific_director<tab>' will be made to complete from a
    list or places that are already remembered from prior usage patterns (some
    of which might be really hard to type the absolute path for).
"""

import os
from IPython.core.magic import Magics, magics_class, line_magic

from smashlib import get_smash
from smashlib.v2 import Reporter
from smashlib.util.events import receives_event
from smashlib.channels import C_CHANGE_DIR
from smashlib.contrib import autojump as _autojump

_main = _autojump.main
parse_arguments = _autojump.parse_arguments


DEFAULT_DATA_FILE = 'autojump.dat'

autojump = lambda x: _main(parse_arguments(args=x))

def j_completer(self, event):
    """ tab completer that queries autojump database"""
    #tmp = event.line.split()[1:]
    options = autojump(['--complete']+\
                event.line.split()[1:])
    return [os.path.split(x.split('__')[-1])[-1] for x in options]

@magics_class
class AutojumpMagics(Magics):
    """ main magics for smash """

    @line_magic
    def j(self, parameter_s=''):
        tmp = parameter_s.split()
        if not tmp:
            return
        if not tmp[0].startswith('-'):
            result = autojump(tmp)
            get_ipython().magic('pushd '+result)
        else:
            try:
                return autojump(tmp)
            except SystemExit:
                pass

class AutojumpPlugin(Reporter):

    def init_magics(self):
        self.shell.register_magics(AutojumpMagics)

    @receives_event(C_CHANGE_DIR)
    def update_weights(self, new_dir, old_dir):
        """ useful as a post-hook for "cd" commands. it might be
            a good idea to call this after the "jump" command or
            after "pushd" as well, but that's not implemented.
        """
        if self.is_updating and new_dir is not None:
            autojump(['--add', new_dir])
            # increment the weight for the current directory.
            # it must be the case that we are already *in* the
            #  directory, because we have received the C_CHANGE_DIR message.
            autojump(['--increase'])
            self.report('autojump '+\
                        "incremented jump-weight for '{0}' to {1}".format(
                            new_dir, '?'))

    def install(self):
        self.is_updating = True
        self.smash.add_completer(j_completer, str_key='j')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = AutojumpPlugin(ip)
    tmp.install()
    return tmp

def unload_ipython_extension(ip):
    get_smash()
    # not implemented
