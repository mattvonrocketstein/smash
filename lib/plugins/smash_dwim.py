""" smash_dwim:

     SmaSh do-what-i-mean plugin allows:

      *  directory-execution:
           Enter in a filepath which is actually a directory, and you
           will be cd'd into that directory.  In fact 'pushd' is used,
           so you can always use 'popd' to get back to where you came
           from.

      * auto-edit for filenames:
          Enter in a filepath which is an editable file but not
          executable, and that file will be opened in the SmaSh
          environment's default editor (provided it isn't too large).

"""

import os
import commands

from IPython.ipapi import TryNext
from smashlib.util import report
from smashlib.smash_plugin import SmashPlugin
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
    cmd = cmd.strip()
    if cmd and cmd[0] in './' and os.path.isfile(cmd):
        if not is_executable(cmd):
            report.smash_dwim("file is not executable; attempting edit")
            if not is_small(cmd):
                report.smash_dwim("file too large, refusing to edit")
            else:
                return __IPYTHON__.magic_ed(cmd)
        else:
            # this file is executable.  the user might want to
            # edit it, but we can't assume that because they
            # might want to execute it.  so, we do nothing.
            pass
    raise TryNext()

class Plugin(SmashPlugin):
    def install(self):
        self.add_hook('shell_hook', executable_dirs_hook, 0)
        self.add_hook('shell_hook', editable_file_hook, 0)
