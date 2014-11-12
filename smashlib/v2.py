""" smashlib.v2
"""

from IPython.config.configurable import Configurable
from IPython.utils.coloransi import TermColors
from IPython.utils.traitlets import Bool
from IPython.utils.traitlets import EventfulList, EventfulDict
from smashlib.logging import Logger

class SmashComponent(object):
    def build_argparser(self):
        import argparse
        parser = argparse.ArgumentParser()
        return parser

    def parse_argv(self):
        import sys
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

class EventfulMix(object):

    def _init_elist(self, name, elist):
        insert_name = '_event_insert_'+name
        set_name = '_event_set_'+name
        del_name = '_event_del_'+name
        kls_name = self.__class__.__name__
        def default_insert(new):
            self.report('default add', new)
        def default_set(slice_or_index, val):
            msg = 'default set (override {0}.{1})'.format(
                kls_name,set_name)
            self.report(msg, slice_or_index, val)
        def default_del(old):
            self.report('default del',old)
        insert_callback = getattr(self, insert_name, default_insert)
        set_callback = getattr(self, set_name, default_set)
        kargs = dict(
            insert_callback=insert_callback,
            set_callback=set_callback,
            del_callback=getattr(self,
                                 del_name,
                                 default_del
                                 ),
            reverse_callback=None,
            sort_callback=None)
        elist.on_events(**kargs)
        # finally, reassign everything so the events get called
        for i in range(len([x for x in elist])):
            elist[i] = elist[i]

    def _get_eventful_type(self, type):
        out = {}
        for name, trait in self.traits().items():
            if isinstance(trait, type):
                out[name] = getattr(self, name)
        return out

    def init_eventful(self):
        # initialize all elists.
        elists = self._get_eventful_type(EventfulList)
        for name, elist in elists.items():
            self._init_elist(name, elist)


class Base(SmashComponent, EventfulMix, Configurable, ):

    def __init__(self, shell, **kargs):
        super(Base, self).__init__(config=shell.config, shell=shell)
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
