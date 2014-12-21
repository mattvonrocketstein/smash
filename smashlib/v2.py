""" smashlib.v2
"""
from collections import defaultdict

from IPython.utils.traitlets import Bool
from IPython.config.configurable import Configurable

from smashlib.logging import Logger
from smashlib.plugins import SmashPlugin
from smashlib.bases.eventful import EventfulMix

class Base(SmashPlugin, EventfulMix, Configurable, ):

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
