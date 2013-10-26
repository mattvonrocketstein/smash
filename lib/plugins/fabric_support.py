""" fabric_support.py

    Install fabric support, which detects and gives relevant advice if
    you change into a directory where a fabric command is present.  Also
    provides tab-completion and direct access to the fabfile's namespace
    via the dynamic variable `_fabric`.
"""

import os

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report, set_complete, post_hook_for_magic

class magic_fabric(object):
    def __init__(self, lazy=True):
        if not lazy:
            fabf = os.path.join(os.getcwd(), 'fabfile.py')
            def thinkaboutit():
                """ this actually loads the methods found in the fabric file into
                    the _fabric namespace (as opposed to simply populating __doc__
                    with the names of those methods).

                    we run in a thread so as not to introduce a long delay and
                    temporarily kill ipython's responsiveness
                """
                tmp = dict(__file__= fabf)
                try:
                   execfile(fabf, tmp)
                except Exception,e:
                    report.magic_fabric("error working with {0}, there may be a fabric version mismatch".format(fabf))
                else:
                   z = self._published_methods
                   tmp = [ [k, tmp[k]] for k in tmp if k in z ]
                   for k,v in tmp:
                       setattr(self, k, v)
            import threading
            threading.Thread(target=thinkaboutit).start()

    @property
    def _published_methods(self):
        """ seriously, it looks like fabric's API does NOT
            provide a better way to do this..
        """
        # cut off the first line,
        # that one just says something like "Available methods:"
        info = [ x.strip() for x in os.popen('fab -l').readlines()[1:] ]
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
        x = self._published_methods
        o = StringIO.StringIO()
        import pprint
        pprint.pprint(x, o)
        o.seek(0)
        return str(x)

    #def __getattr__(self, name):

    @classmethod
    def install_into_ipython(kls):
        __IPYTHON__.shell.user_ns.update(_fabric=magic_fabric())
        post_hook_for_magic('cd', look_for_fabfile)

def look_for_fabfile():
    if 'fabfile.py' in os.listdir(os.getcwd()):
        report.fabric_support('Discovered fabfile.  '
                              'Type "_fabric?" to list commands')
        __IPYTHON__.shell.user_ns.update(_fabric=magic_fabric(lazy=False))


def fab_completer(self, event):
    data = event.line.split()[1:] # e.g. 'git',' mv', './<tab>'
    names = magic_fabric()._published_methods
    # no info: complete from all the names
    if not data:
        return names
    else:
        return [x for x in names if x.startswith(data[-1])]


class Plugin(SmashPlugin):
    def install(self):
        magic_fabric.install_into_ipython()
        set_complete(fab_completer, 'fab')
