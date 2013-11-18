""" smash_dwim:

     SmaSh do-what-i-mean plugin allows "execution" of directories by
     changing directory to them.  In fact 'pushd' is used, so you can
     use 'popd' to get back to where you came from.

"""

import os
import commands

from IPython.ipapi import TryNext
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report
from smashlib.python import isdir

EDITABLE_FILE_SIZE_THRESH = 32768

def is_executable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def executable_dirs_hook(cmd):
    """ """
    cmd = cmd.strip()
    if cmd and cmd[0] in './' and isdir(cmd):
        report.plugin_dwim("entering: "+ cmd)
        return __IPYTHON__.magic_pushd(cmd)
    raise TryNext()

def is_small(fname):
    return os.path.getsize(fname) < EDITABLE_FILE_SIZE_THRESH

def editable_file_hook(cmd):
    report('yo trying')
    cmd = cmd.strip()
    if cmd and cmd[0] in './' and os.path.isfile(cmd):
        report('still')
        if not is_executable(cmd):
            report('still2')
            report.smash_dwim("file is not executable; attempting edit")
            if not is_small(cmd):
                report.smash_dwim("file too large, refusing to edit")
            else:
                return __IPYTHON__.magic_ed(cmd)
        else:
            pass #
    raise TryNext()

class Plugin(SmashPlugin):
    def install(self):
        self.add_hook('shell_hook', executable_dirs_hook, 0)
        self.add_hook('shell_hook', editable_file_hook, 0)
