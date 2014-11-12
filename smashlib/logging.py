""" smashlib.logging
"""
from smashlib.util.ipy import TermColors

class Logger(object):
    def __init__(self, component):
        self.component = component

    @property
    def verbose(self):
        return self.component.verbose

    @property
    def ignore_warnings(self):
        return self.component.smash.ignore_warnings

    @property
    def ignore_info(self):
        return False

    def report(self, msg, *args, **kargs):
        force = kargs.pop('force', False)
        if self.verbose or force:
            header = kargs.pop('header','')
            header = self.component.__class__.__name__ + ':' + header
            header = TermColors.Blue + header
            content = TermColors.Red + msg
            print "{0}: {1} {2}".format(
                header, content, TermColors.Normal)
            if args:
                print '  ',args

    def warning(self,*args, **kargs):
        if not self.ignore_warnings:
            kargs['force'] = True
            kargs['header'] = 'warning'
            self.report(*args, **kargs)

    def info(self, *args, **kargs):
        if not self.ignore_info:
            kargs['force'] = True
            #kargs['header'] = ''
            self.report(*args, **kargs)
