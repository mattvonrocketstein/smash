"""
"""
from IPython.ipapi import TryNext
from smashlib.smash_plugin import SmashPlugin

def executable_dirs_hook(cmd):
    """ """
    cmd = cmd.strip()
    if cmd and cmd[0] in './' and os.path.isdir(cmd):
        return __IPYTHON__.magic_pushd(cmd)
    raise TryNext()

#def editable_files_hook)
class Plugin(SmashPlugin):

    def install(self):
        __IPYTHON__.hooks.shell_hook.add(executable_dirs_hook,0)
