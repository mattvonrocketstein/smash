""" smash.plugins.plugin
"""
import sys
import argparse

from IPython.core.macro import Macro

class SmashPlugin(object):
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

    def contribute_hook(self, name, fxn):
        """ contributes a hook to ipython and
            records it so it can be inverted later
        """
        self.shell.set_hook(name, fxn)
        self.installation_record['hooks'] += [[name, fxn]]

    def uninstall(self):
        """ uninstall this smash component """
        self.report("uninstalling myself")
        self._uninstall_magics()
        self._uninstall_hooks()

    def _uninstall_hooks(self):
        """ uninstall all hooks which were installed by "self.contribute_hook"
        """
        for name, fxn in self.installation_record['hooks']:
            self.report("uninstalling hook: {0}".format(name))
            callchain = self.shell.hooks[name].chain
            # HACK: cannot figure out another way to unregister items from the callchain
            #       registry rebinds instance methods and screws with the normal values
            #       for self.im_class, etc
            new_callback = []
            for priority, cfxn in callchain:
                if cfxn.__name__ == fxn.__name__:
                    continue
                new_callback.append([priority,cfxn])
        self.shell.hooks[name].chain = new_callback

    def _uninstall_magics(self):
        """ uninstall all magics which were installed by "self.contribute_magic"
        """
        for m in self.installation_record['magics']:
            self.report("uninstalling magic: {0}".format(m))
            del self.shell.magics_manager.magics['line'][m.__name__]

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
Plugin = SmashPlugin
