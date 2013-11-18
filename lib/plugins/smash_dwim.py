""" smash_dwim:

     SmaSh do-what-i-mean plugin allows "execution" of directories by
     changing directory to them.  In fact 'pushd' is used, so you can
     use 'popd' to get back to where you came from.

"""

from IPython.ipapi import TryNext
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report
from smashlib.python import isdir

def executable_dirs_hook(cmd):
    """ """
    cmd = cmd.strip()
    if cmd and cmd[0] in './' and isdir(cmd):
        report.plugin_dwim("entering: "+ cmd)
        return __IPYTHON__.magic_pushd(cmd)
    raise TryNext()

class Plugin(SmashPlugin):
    def install(self):
        self.add_hook('shell_hook', executable_dirs_hook, 0)
