""" exec_dirs:

     SmaSh plugin that allows "execution" of directories by changing directory
     to them.  In fact 'pushd' is used, so you can use 'popd' to get back to where
     you came from.
"""

from IPython.ipapi import TryNext
from smashlib.smash_plugin import SmashPlugin

def executable_dirs_hook(cmd):
    """ """
    cmd = cmd.strip()
    if cmd and cmd[0] in './' and os.path.isdir(cmd):
        return __IPYTHON__.magic_pushd(cmd)
    raise TryNext()

class Plugin(SmashPlugin):
    def install(self):
        self.add_hook('shell_hook', executable_dirs_hook, 0)
