""" smashlib.patches.pinfo
"""
from smashlib.patches.base import PatchMagic
from smashlib import get_smash

class PatchPinfoMagic(PatchMagic):
    name = 'pinfo'

    def __call__(self, parameter_s=''):
        tmp = parameter_s.replace('?', '')
        user_magics = self.shell.magics_manager.user_magics
        is_magic = magic_cmd = getattr(user_magics, tmp, None)
        if is_magic:
            obj = magic_cmd
        else:
            # lookup using generic object
            tmp = parameter_s.replace('?', '').split('.')
            obj = self.shell.user_ns.get(tmp.pop(0))
            while tmp:
                obj = getattr(obj, tmp.pop(0))
        if hasattr(obj, '__qmark__'):
            try:
                print obj.__qmark__()
            except:
                raise #print 'error with qmark protocol in ' + str(obj)
            return
        else:
            return self.original(parameter_s)
