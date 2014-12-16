""" smashlib.v2
"""
import sys
import argparse
from IPython.utils.traitlets import Bool
from IPython.config.configurable import Configurable
from IPython.core.macro import Macro

from smashlib.logging import Logger
from smashlib.bases.eventful import EventfulMix
from collections import defaultdict
class SmashComponent(object):
    def build_argparser(self):
        parser = argparse.ArgumentParser()
        return parser

    def __qmark__(self):
        return self.__doc__ or '{0} has no __qmark__(), no __doc__()'.format(self)

    def install(self):
        pass

    def contribute_magic(self, fxn):
        # TODO: verify signature?
        self.installation_record['magics']+=[fxn]
        return self.smash.shell.magics_manager.register_function(fxn)

    def contribute_macro(self, name, macro):
        if isinstance(macro, list):
            macro = '\n'.join(macro)
        if isinstance(macro, basestring):
            macro = Macro(macro)
        if not isinstance(macro, Macro):
            err = "expected input would be string, list of strings, or Macro"
            raise TypeError(err)
        if not isinstance(name, basestring):
            err = "macro's name must be a string!"
            raise TypeError(err)
        macro.name = name
        self.shell.user_ns[name] = macro
        self.installation_record['macros']+=[macro]

    def parse_argv(self):
        parser = self.build_argparser()
        args, unknown = parser.parse_known_args(sys.argv[1:])
        if len(vars(args)):
            self.report("parsed argv: "+str(args))
        return args, unknown

    @property
    def smash(self):
        try:
            return self.shell._smash
        except AttributeError:
            raise Exception("load smash first")

    @property
    def publish(self):
        return self.smash.bus.publish


class Base(SmashComponent, EventfulMix, Configurable, ):

    def __init__(self, shell, **kargs):
        super(Base, self).__init__(config=shell.config, shell=shell)

        # plugins should use self.contribute_* commands, which update the installation
        # record automatically.  later the installation record will help with uninstalling
        # plugins cleanly and completely
        self.installation_record = defaultdict(list)

        self.shell.configurables.append(self)
        self.init_logger()
        self.report("initializing {0}".format(self))
        self.init_eventful()
        self.init_bus()
        self.init_magics()
        self.init()

    def init_magics(self):
        pass

    def init_logger(self):
        self.logger = Logger(self)
        self.report = self.logger.report
        self.warning = self.logger.warning
        self.info = self.logger.info

    def __str__(self):
        return '<SmashExtension: {0}>'.format(self.__class__.__name__)
    __repr__ = __str__


    def init(self):
        pass

    def init_bus(self):
        """ register any instance methods that
            have used the receives_event decorator
        """
        for x in dir(self):
            # look through the class to avoid
            # triggering properties on the instance
            obj = getattr(self.__class__, x, None)
            channel = getattr(obj, '_subscribe_to', None)
            if channel:
                # since we looked through the class earlier,
                # we need to actually retrieve the method now
                y = getattr(self, x)
                self.smash.bus.subscribe(channel, y)


class Reporter(Base):
    verbose = Bool(False, config=True)
