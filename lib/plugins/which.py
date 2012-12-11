""" replace the unix shell's "which" command with a smarter
    drop-in replacement.

    protocol w.r.t to "which" when applied to argument "name":
      1) return the output unix-which for "name" if that's nonempty
      2) return file for obj "name" if it's in the global namespace
      3) return the file for module "name", if such a module is available
"""
import sys, os, inspect
from smashlib.smash_plugin import SmashPlugin

def which(name):
    cmd = os.popen('which '+name).read().strip()
    if cmd:
        return cmd
    else:
        if name in __IPYTHON__.user_ns:
            obj = __IPYTHON__.user_ns[name]
            try: return inspect.getfile(obj)
            except TypeError:
                try:
                    return inspect.getfile(obj.__class__)
                except TypeError,e:
                    return str(e)
        else:
            if name in sys.modules:
                return sys.modules['name']
            return 'error: Name {0} known to none of shell / interpretter / module search path'.format(name)

class Plugin(SmashPlugin):
    """
    """
    def install(self):
        def magic_which(parameter_s=''):
            return which(parameter_s)
        self.contribute_magic('which', magic_which)
