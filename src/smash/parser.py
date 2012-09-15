""" smash.parser
"""

from optparse import OptionParser

from smash import Plugins

class SmashParser(OptionParser):

    extra_options = []

    @classmethod
    def defer_option(cls, args=None, kargs=None, handler=None):
        cls.extra_options.append([args, kargs, handler])

    def __init__(self, *args, **kargs):
        OptionParser.__init__(self, *args, **kargs)
        self.add_option("-v", dest="verbose", action="store_true",
                          default=False, help='more verbose bootstrapping info')
        self.add_option("--panic", dest="panic",
                          default=False, action="store_true",
                          help="kill all running instances of 'smash'", )
        self.add_option('-i', '--install',
                          dest='install', default='',
                          help='install new smash module')
        self.add_option('-l', '--list',
                          action='store_true',dest='list', default=False,
                          help=Plugins.list.__doc__)
        self.add_option('--enable',
                          dest='enable', default='',
                          help=Plugins.enable.__doc__)
        self.add_option('--disable',
                          dest='disable', default='',
                          help=Plugins.disable.__doc__)
        for args, kargs,handler in self.extra_options:
            self.add_option(*args, **kargs)
