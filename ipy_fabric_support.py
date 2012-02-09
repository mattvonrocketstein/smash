""" ipy_fabric_support
"""

import os

from ipy_bonus_yeti import post_hook_for_magic

class magic_fabric(object):
    def __init__(self, lazy=True):
        if not lazy:
            def thinkaboutit():
                tmp = {}
                execfile('fabfile.py', tmp)
                z = self.__published_methods
                tmp = [ [k, tmp[k]] for k in tmp if k in z ]
                for k,v in tmp:
                    setattr(self,k,v)
            import threading
            threading.Thread(target=thinkaboutit).start()

    @property
    def __published_methods(self):
        """ seriously, it looks like fabric's API does NOT
            provide a better way to do this..
        """
        info = [ x.strip() for x in os.popen('fab -l').readlines() ]
        info = filter(None, info)
        for oline in info:
            try:
                line = oline.split()[0]
            except IndexError:
                info.remove(line)
            else:
                info[info.index(oline)] = line
        info = info[1:]
        return info

    @property
    def __doc__(self):
        """ this amounts to an __init__ method, so it might seem
            like it's in a strange place.  the reason why is because
            of ipython's object inspection / reporting that is triggered
            by the '?' modifier at the end of a line.

            _fabric
        """
        import StringIO
        x = self.__published_methods
        o = StringIO.StringIO()
        import pprint
        pprint.pprint(x, o)
        o.seek(0)
        return str(x)

    #def __getattr__(self, name):

    @classmethod
    def install_into_ipython(kls):
        __IPYTHON__.shell.user_ns.update(_fabric=magic_fabric())


def look_for_fabfile():
    if 'fabfile.py' in os.listdir(os.getcwd()):
        print 'Discovered fabfile.  Type "_fabric?" to list commands'
        __IPYTHON__.shell.user_ns.update(_fabric=magic_fabric(lazy=False))

post_hook_for_magic('cd', look_for_fabfile)
