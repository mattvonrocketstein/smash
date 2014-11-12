""" smashlib.ipy_smash

    Defines the main smash extension, which itself loads and
    allows communications between the other smash extensions.

    TODO: dynamic loading of extensions (use EventfulList)
"""
import os
import cyrusbus

from IPython.utils.traitlets import EventfulList, List, Bool

from smashlib.v2 import Reporter
from smashlib.channels import C_POST_RUN_INPUT, C_POST_RUN_CELL
from smashlib.util.reflect import from_dotpath, ObjectNotFound
from smashlib.util.events import receives_event
from smashlib.util import bash
from smashlib import logging

from IPython.core.magic import Magics, magics_class, line_magic

@magics_class
class SmashMagics(Magics):
    @line_magic
    def ed_config(self, parameter_s=''):
        from smashlib.data import USER_CONFIG_PATH
        self.shell.magic('ed {0}'.format(USER_CONFIG_PATH))

class Smash(Reporter):
    extensions = List(default_value=[], config=True)
    verbose_events = Bool(False, config=True)
    ignore_warnings = Bool(False, config=True)
    load_bash_aliases = Bool(False, config=True)

    def system(self, cmd, quiet=False):
        from smashlib.util._fabric import qlocal
        if not quiet:
            self.report("run: "+cmd)
        return qlocal(cmd, capture=True)

    def init_magics(self):
        self.shell.register_magics(SmashMagics)

    def init_extensions(self):
        record = {}
        for dotpath in self.extensions:
            mod = from_dotpath(dotpath)
            ext_name = dotpath.split('.')[-1]
            ext_obj = mod.load_ipython_extension(self.shell)
            record[ext_name] = ext_obj
            if ext_obj is None:
                msg = '{0}.load_ipython_extension should return an object'
                msg = msg.format(dotpath)
                self.warning(msg)
        self.loaded_extensions = record
        self.report("loaded extensions:", self.loaded_extensions.keys())

    def build_argparser(self):
        parser = super(Smash, self).build_argparser()
        parser.add_argument('-c','--command', default='')
        return parser

    def parse_argv(self):
        """ parse arguments recognized by myself,
            then let all the extensions take a stab
            at it.
        """
        main_args, unknown = super(Smash,self).parse_argv()
        ext_objs = self.loaded_extensions.values()
        for obj in ext_objs:
            if obj:
                args,unknown = obj.parse_argv()
        if main_args.command:
            self.shell.run_cell(main_args.command)
            self.shell.run_cell('exit')

    @property
    def project_manager(self):
        return self.loaded_extensions['ipy_project_manager']

    def init(self):
        self.shell._smash = self
        self.init_bus()
        self.init_extensions()
        self.parse_argv()
        if self.load_bash_aliases:
            for alias, cmd in bash.get_aliases():
                if alias not in 'ed cd'.split(): #HACK
                    self.shell.magic("alias {0} {1}".format(alias,cmd))

        smash_bin = os.path.expanduser('~/.smash/bin')
        if smash_bin not in os.environ['PATH']:
            os.environ['PATH'] =smash_bin + ':' + os.environ['PATH']

    def init_bus(self):
        """ note: it is a special case that due to bootstrap ordering,
            @receive_events is not possible for this class.  if you want
            to register event callbacks you'll have to register everything
            the simple way.
        """
        super(Smash,self).init_bus()
        bus = cyrusbus.Bus()
        def warning_dep(*args, **kargs):
            raise Exception("dont send warning that way")
        bus.subscribe('warning', warning_dep)
        bus.subscribe(C_POST_RUN_INPUT, self.input_finished_hook)
        self.bus = bus

    def input_finished_hook(self, bus, raw_finished_input):
        if not raw_finished_input.strip():
            return
        rehash_if = [
            'setup.py develop',
            'pip install',
            'setup.py install',
            'apt-get install']
        for x in rehash_if:
            if x in raw_finished_input:
                self.report("detected possible $PATH changes (rehashing)")
                self.shell.magic('rehashx')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    ip._smash = Smash(ip)
    return ip._smash

def unload_ipython_extension(ip):
    del ip._smash
