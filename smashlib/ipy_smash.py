""" smashlib.ipy_smash

    Defines the main smash plugin, which itself loads and
    allows communications between the other smash plugins.

    TODO: dynamic loading of plugins (use EventfulList)
"""
import os
import cyrusbus
from collections import defaultdict

from IPython.utils.traitlets import List, Bool

from smashlib.v2 import Reporter
from smashlib.util.reflect import from_dotpath
from smashlib.util import bash
from smashlib.magics import SmashMagics
from smashlib.channels import C_SMASH_INIT_COMPLETE
from smashlib.plugins.interface import PluginInterface
from smashlib.patches.edit import PatchEdit
from smashlib.patches.pinfo import PatchPinfoMagic
from smashlib.util._fabric import qlocal

class Smash(Reporter):
    plugins             = List(default_value=[], config=True)
    verbose_events      = Bool(False, config=True)
    ignore_warnings     = Bool(False, config=True)
    load_bash_aliases   = Bool(False, config=True)
    load_bash_functions = Bool(False, config=True)

    bus                = cyrusbus.Bus()
    error_handlers     = []
    _installed_plugins = {}
    completers         = defaultdict(list)

    def _repr_pretty_(self, p, cycle):
        """ demo that behaves just like repr()"""
        p.text(repr(self))

    def system(self, cmd, quiet=False):
        print 'yap',cmd
        if not quiet:
            self.report("run: " + cmd)
        return qlocal(cmd, capture=True)

    def init_magics(self):
        self.shell.register_magics(SmashMagics)

    def init_plugins(self):
        _installed_plugins = {}
        for dotpath in self.plugins:
            mod = from_dotpath(dotpath)
            ext_name = dotpath.split('.')[-1]
            ext_obj = mod.load_ipython_extension(self.shell)
            _installed_plugins[ext_name] = ext_obj
            if ext_obj is None:
                msg = '{0}.load_ipython_extension should return an object'
                msg = msg.format(dotpath)
                self.warning(msg)
        self._installed_plugins = _installed_plugins
        plugin_iface = PluginInterface(self)
        plugin_iface.update()
        get_ipython().user_ns.update(plugins=plugin_iface)
        self.report("loaded plugins:", _installed_plugins.keys())

    def build_argparser(self):
        parser = super(Smash, self).build_argparser()
        # thinking of adding extra parsing here?  think twice.
        # whatever you're doing probably belongs in a plugin..
        return parser

    def parse_argv(self):
        """ parse arguments recognized by myself,
            then let all the plugins take a stab
            at it.
        """
        main_args, unknown = super(Smash,self).parse_argv()
        ext_objs = self._installed_plugins.values()
        for obj in ext_objs:
            if obj:
                args, unknown = obj.parse_argv()

    @property
    def project_manager(self):
        return self._installed_plugins['project_manager']

    def init(self):
        self.shell._smash = self
        self.init_bus()
        self.init_plugins()
        self.parse_argv()
        self.init_config_inheritance()
        smash_bin = os.path.expanduser('~/.smash/bin')
        if smash_bin not in os.environ['PATH']:
            os.environ['PATH'] = smash_bin + ':' + os.environ['PATH']

        self.init_patches()
        self.publish(C_SMASH_INIT_COMPLETE)

    def init_config_inheritance(self):
        if self.load_bash_aliases:
            for alias, cmd in bash.get_aliases():
                # this check is a hack, but users will frequently override
                # cd to pushd which is already done in smash anyway
                if alias not in 'ed cd'.split():
                    self.shell.magic("alias {0} {1}".format(alias,cmd))

        if self.load_bash_functions:
            fxns = bash.get_functions()
            for fxn_name in fxns:
                cmd = bash.FunctionMagic(fxn_name)
                self.shell.magics_manager.register_function(cmd, magic_name=fxn_name)
            self.report("registered magic for bash functions: ",fxns)


    def init_patches(self):
        PatchEdit(self).install()
        PatchPinfoMagic(self).install()

    def init_bus(self):
        """ note: it is a special case that due to bootstrap ordering,
            @receive_events is not possible for this class.  if you want
            to register event callbacks you'll have to register everything
            the simple way.
        """
        super(Smash, self).init_bus()

    def add_completer(self, fxn, **kargs):
        from goulash._inspect import get_caller
        self.completers[get_caller(2)['class']].append(fxn)
        get_ipython().set_hook('complete_command', fxn, **kargs)

def load_ipython_extension(ip):
    """ called by %load_ext magic """
    ip = get_ipython()
    ip._smash = Smash(ip)
    return ip._smash

def unload_ipython_extension(ip):
    del ip._smash
