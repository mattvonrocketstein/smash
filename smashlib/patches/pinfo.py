""" smashlib.patches.pinfo
"""
from smashlib.patches.base import PatchMagic

class PatchPinfoMagic(PatchMagic):
    name = 'pinfo'
    def __call__(self, parameter_s=''):
        tmp = parameter_s.replace('?','').split('.')
        obj = self.component.shell.user_ns.get(tmp.pop(0))
        while tmp:
            obj = getattr(obj, tmp.pop(0))
        if hasattr(obj, '__qmark__'):
            try:
                print obj.__qmark__()
            except:
                print 'error with qmark protocol in '+str(obj)
            return
        else:
            return self.original(parameter_s)
