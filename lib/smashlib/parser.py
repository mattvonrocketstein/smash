""" smashlib.parser
"""

import new
from optparse import OptionParser, BadOptionError

from smashlib.util import report, report_if_verbose
from smashlib import PluginManager


# from: http://stackoverflow.com/questions/1885161/how-can-i-get-optparses-optionparser-to-ignore-invalid-options
class PassThroughOptionParser(OptionParser):
    def _process_long_opt(self, rargs, values):
        try:
            OptionParser._process_long_opt(self, rargs, values)
        except BadOptionError, err:
            self.largs.append(err.opt_str)

    def _process_short_opts(self, rargs, values):
        try:
            OptionParser._process_short_opts(self, rargs, values)
        except BadOptionError, err:
            self.largs.append(err.opt_str)

class SmashParser(OptionParser):

    # populated by plugins (options will be parsed on the second-pass)
    extra_options = []

    @classmethod
    def defer_option(cls, args=None, kargs=None, handler=None):
        cls.extra_options.append([args, kargs, handler])

    def __init__(self, *args, **kargs):
        strict = kargs.pop('strict', True)
        if not strict:
            #report_if_verbose.parser('strict parsing disabled')
            self._process_long_opt = new.instancemethod(PassThroughOptionParser._process_long_opt.im_func,
                                                        self,self.__class__)
            self._process_short_opts = new.instancemethod(PassThroughOptionParser._process_short_opts.im_func,
                                                          self,self.__class__)
        OptionParser.__init__(self, *args, **kargs)
        from smashlib.util import panic
        self.add_option("-v", dest="verbose", action="store_true",
                          default=False, help='more verbose bootstrapping info')
        self.add_option("--panic", dest="panic",
                          default=False, action="store_true",
                          help=panic.__doc__, )
        self.add_option('-i', '--install',
                          dest='install', default='',
                          help=PluginManager.cmdline_install_new_plugin.__doc__)
        self.add_option('-l', '--list',
                          action='store_true', dest='list', default=False,
                          help=PluginManager.cmdline_list.__doc__)
        self.add_option('--enable',
                          dest='enable', default='',
                          help=PluginManager.cmdline_enable.__doc__)
        self.add_option('--disable',
                          dest='disable', default='',
                          help=PluginManager.disable.__doc__)
        for args, kargs,handler in self.extra_options:
            self.add_option(*args, **kargs)
