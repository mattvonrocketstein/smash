""" replace the unix shell's "which" command with a smarter
    drop-in replacement.

    protocol for "which" when applied to argument "name":
      1) return the output unix-which for "name" if that's nonempty
      2) return file for obj "name" if it's in the global namespace
      3) return the file for module "name", if such a module is available
"""
import sys, os, inspect
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report
def which(name):
    ("replaces the unix shell's \"which\" command "
     "with a smarter drop-in replacement.\n\n"
     "standard protocol for \"which\" when applied to argument \"name\":\n\n"
      "1) return the output unix-which for \"name\" if that's nonempty\n"
      "2) return file for obj \"name\" if it's in the global namespace\n"
      "3) return the file for module \"name\", if such a module is available\n")

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
            try:
                obj = eval(name)
            except:
                if name in sys.modules:
                    return sys.modules['name']
                else:
                    try: return __import__(name)
                    except:
                        report.which(('Name {0} known to none of '
                                     'shell / interpretter / module '
                                     'search path').format(name))
            else:
                return inspect.getfile(obj)

class Plugin(SmashPlugin):
    """
    """
    def install(self):
        def magic_which(parameter_s=''):
            return which(parameter_s)
        magic_which.__doc__=which.__doc__
        self.unalias('which')
        self.contribute_magic('which', magic_which)
