""" smashlib.ipy_smash

    Defines the main smash plugin, which itself loads and
    allows communications between the other smash plugins.

    TODO: dynamic loading of plugins (use EventfulList)
"""
import os
import cyrusbus
import argparse

from itertools import imap
from operator import itemgetter
from collections import defaultdict

from goulash._fabric import qlocal
from goulash._inspect import get_caller

from IPython.utils.traitlets import List, Bool

from smashlib import data
from smashlib.plugins import Plugin
from smashlib.util.reflect import from_dotpath
from smashlib.util import bash
from smashlib.magics import SmashMagics
from smashlib.channels import C_SMASH_INIT_COMPLETE
from smashlib.plugins.interface import PluginInterface
from smashlib.prompt.interface import PromptInterface
from smashlib.patches.edit import PatchEdit
from smashlib.patches.rehash import PatchRehash
from smashlib.patches.pinfo import PatchPinfoMagic
from smashlib._logging import smash_log

from smashlib.aliases import AliasInterface


class Smash(Plugin):
    plugins = List(default_value=[], config=True)
    verbose_events = Bool(True, config=True)
    ignore_warnings = Bool(False, config=True)
    load_bash_aliases = Bool(False, config=True)
    load_bash_functions = Bool(False, config=True)

    bus = cyrusbus.Bus()
    error_handlers = []
    _installed_plugins = {}
    completers = defaultdict(list)

    def _repr_pretty_(self, p, cycle):
        """ demo that behaves just like repr()"""
        p.text(repr(self))

    def system(self, cmd, quiet=False):
        #self.report("run: " + cmd, force=True)
        return qlocal(cmd, capture=True)

    def init_magics(self):
        self.shell.register_magics(SmashMagics)

    def init_plugins(self):
        _installed_plugins = {}
        from smashlib.plugins import Plugin
        for dotpath in self.plugins:
            try:
                mod = from_dotpath(dotpath)
            except AttributeError as e:
                err = "Error working with plugin {0}: {1}"
                err = err.format(dotpath, e)
                self.report(err)
                self.logger.warning(err)
                continue
            ext_name = dotpath.split('.')[-1]
            ext_obj = mod.load_ipython_extension(self.shell)
            assert isinstance(ext_obj, Plugin), \
                ("error with extension '{0}': smash requires load_ipython_extension()"
                 " to return plugin object ").format(ext_name)
            _installed_plugins[ext_name] = ext_obj
            if ext_obj is None:
                msg = '{0}.load_ipython_extension should return an object'
                msg = msg.format(dotpath)
                self.warning(msg)
        self._installed_plugins = _installed_plugins

        tmp = [AliasInterface, PluginInterface, PromptInterface]
        for IfaceCls in tmp:
            iface = IfaceCls(self)
            iface.update()
            get_ipython().user_ns.update({iface.user_ns_var:iface})


        #alias_iface = AliasInterface(self)
        #alias_iface.update()
        #get_ipython().user_ns.update(aliases=alias_iface)

        #plugin_iface = PluginInterface(self)
        #plugin_iface.update()
        #get_ipython().user_ns.update(plugins=plugin_iface)
        self.report("loaded plugins:", _installed_plugins.keys())

    def get_cli_arguments(self):
        return [[['--version', ], dict(default=False, action='store_true')]]

    def build_argparser(self):
        """ builds the main smash cl-option parser,
            based on data from plugins.  this is weird,
            because we have to bootstrap all the plugins
            long before parsing command line options, but
            is very flexible since it allows the plugins
            themselves to modify command line options.
        """
        parser = argparse.ArgumentParser()
        plugins = [self] + self._installed_plugins.values()
        for plugin in plugins:
            clopts = plugin.get_cli_arguments()
            for clopt in clopts:
                args, kargs = clopt
                if not isinstance(args, (list, tuple)) or \
                   not isinstance(kargs, dict):
                    err = "{0} has not implemented get_cli_arguments correctly"
                    err = err.format(plugin)
                    raise SystemExit(err)
                parser.add_argument(*args, **kargs)
        #import argcomplete
        # argcomplete.autocomplete(parser)

        # thinking of adding extra parsing here?  think twice.
        # whatever you're doing probably belongs in a separate plugin
        return parser

    def use_argv(self, args):
        if args.version:
            from smashlib.version import __version__ as version
            print version
            self.shell.exit()

    def parse_argv(self):
        """ parse arguments recognized by myself,
            then let all the plugins take a stab at it.
        """
        parser = self.build_argparser()
        args = parser.parse_args()
        plugins = [self] + self._installed_plugins.values()
        for plugin in plugins:
            plugin.use_argv(args)
        return args

    @property
    def project_manager(self):
        return self._installed_plugins['project_manager']

    def init(self):
        self.shell._smash = self
        self.init_bus()
        self.init_plugins()
        try:
            self.parse_argv()
        except SystemExit:
            self.shell.exit()
        self.init_macros()
        self.init_config_inheritance()
        if data.SMASH_BIN not in os.environ['PATH']:
            os.environ['PATH'] = data.SMASH_BIN + ':' + os.environ['PATH']
        self.init_patches()
        self.publish(C_SMASH_INIT_COMPLETE)
        self.shell.user_ns['_smash'] = self
        self.shell.run_cell('rehashx')
        # self.user_ns.pop('')

    def recent_commands(self, num):
        tmp = self.history(num)
        return set(list(tmp))

    def history(self, num):
        tmp = self.shell.history_manager.get_tail(num)
        # ipython history includes session id and input number,
        # whereas this only returns the input-lines
        return imap(itemgetter(-1), tmp)

    def init_macros(self):
        # suport export foo=bar
        # macro is used here because setting
        # an alias for an alias does not work
        self.contribute_macro(
            'export',
            ["tmp = get_ipython()._last_input_line;",
             "get_ipython().magic(tmp.replace('export','set_env'));"])

        # use bash reset instead of python reset.
        # a macro is used here because macros are honored
        # before aliases and this overrides a preexisting
        # (but less useful) ipython alias
        self.contribute_macro(
            'reset',
            "get_ipython().system('reset')")

    def init_config_inheritance(self):
        if self.load_bash_aliases:
            for alias, cmd in bash.get_aliases():
                # this check is a hack, but users will frequently override
                # cd to pushd which is already done in smash anyway
                if alias not in 'ed cd'.split():
                    self.shell.magic("alias {0} {1}".format(alias, cmd))

        if self.load_bash_functions:
            smash_log.info("Loading bash functions")
            fxns = bash.get_functions()
            for fxn_name in fxns:
                cmd = bash.FunctionMagic(fxn_name)
                self.shell.magics_manager.register_function(
                    cmd, magic_name=fxn_name)
            msg = "registered magic for bash functions: " + str(fxns)
            smash_log.info(msg)
            self.report(msg)

    def init_patches(self):
        PatchEdit(self).install()
        PatchPinfoMagic(self).install()
        PatchRehash(self).install()

    def init_bus(self):
        """ note: it is a special case that due to bootstrap ordering,
            @receive_events is not possible for this class.  if you want
            to register event callbacks you'll have to register everything
            the simple way.
        """
        super(Smash, self).init_bus()

    def add_completer(self, fxn, **kargs):
        smash_log.info("adding new completer: {0}".format(fxn))
        self.completers[get_caller(2)['class']].append(fxn)
        get_ipython().set_hook('complete_command', fxn, **kargs)


def load_ipython_extension(ip):
    """ called by %load_ext magic """
    ip = get_ipython()
    ip._smash = Smash(ip)
    return ip._smash
