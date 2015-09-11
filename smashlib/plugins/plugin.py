""" smash.plugins.plugin

    NB: plugin related obviously, but this is not a plugin.
        it's the abstract classes for creating subclasses
"""
from collections import defaultdict

from IPython.core.macro import Macro
from IPython.utils.traitlets import Bool
from IPython.config.configurable import Configurable

from smashlib._logging import Logger, events_log, smash_log
from smashlib.bases.eventful import EventfulMix
from smashlib._logging import smash_log

class APlugin(object):

    """ """

    def get_cli_arguments(self):
        return []

    def __qmark__(self):
        return self.__doc__ or '{0} has no __qmark__(), no __doc__()'.format(self)

    def install(self):
        return self

    def contribute_completer(self, key, fxn):
        self.installation_record['completers'].append([key, fxn])
        self.smash.add_completer(fxn, re_key=key)

    def contribute_magic(self, fxn):
        # TODO: verify signature?
        self.installation_record['magics'] += [fxn]
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
        self.installation_record['macros'] += [macro]

    def contribute_hook(self, name, fxn):
        """ contributes a hook to ipython and
            records it so it can be inverted later
        """
        self.shell.set_hook(name, fxn)
        self.installation_record['hooks'] += [[name, fxn]]

    @property
    def smash(self):
        try:
            return self.shell._smash
        except AttributeError:
            raise Exception("load smash first")

    def publish(self, *args, **kargs):
        events_log.info("{0} {1} {2}".format(self, args, kargs))
        return self.smash.bus.publish(*args, **kargs)


class SmashPlugin(APlugin, EventfulMix, Configurable, ):

    verbose = Bool(False, config=True)
    plugin_instance = None

    def __init__(self, shell, **kargs):
        if self.plugin_instance:
            raise Exception,'singleton'
        super(SmashPlugin, self).__init__(config=shell.config, shell=shell)

        # plugins should use self.contribute_* commands, which update the installation
        # record automatically.  later the installation record will help with uninstalling
        # plugins cleanly and completely
        self.installation_record = defaultdict(list)

        self.shell.configurables.append(self)
        self.init_logger()
        smash_log.info("initializing {0}".format(self))
        self.init_eventful()
        self.init_bus()
        self.init_magics()
        self.init()
        self.plugin_instance = self

    def init_magics(self):
        pass

    def use_argv(self, args):
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
                callback = getattr(self, x)
                data = self.smash.bus.subscriptions.get(channel, [])
                callbacks = [
                    [z['callback'].__name__,
                     z['callback'].im_self.__class__] for z in \
                    reduce(lambda x, y: x + y,
                           self.smash.bus.subscriptions.values(),[]
                           )]
                cbname = callback.__name__
                klass = self.__class__
                if [cbname, klass] in callbacks:
                    # this means init_bus was called
                    # twice for the plugin, or something like that
                    smash_log.warning(
                        ('refusing to register what looks '
                        'like a duplicate callback: {0}').format(
                            dict(name=cbname,
                                 klass=klass,
                                 channel=channel)))
                else:
                    self.smash.bus.subscribe(channel, callback)
