""" smashlib.project_manager
"""
import os
import inspect
from IPython.utils.traitlets import EventfulDict, EventfulList, Set

from report import console
from smashlib.channels import (
    C_SMASH_INIT_COMPLETE, C_CHANGE_DIR,
    C_REHASH_EVENT, C_DOT_CMD)

from smashlib.project_manager.util import (
    clean_project_name, UnknownProjectError)
from goulash.python import abspath, expanduser, getcwd, ope
from smashlib.util import guess_dir_type
from smashlib.util.events import receives_event
from smashlib.util.ipy import green
from smashlib.v2 import Reporter

from smashlib.project_manager.magics import ProjectMagics

from .interface import ProjectManagerInterface
from .operation import OperationStep,NullOperationStep
from .activate import Activation, NullActivation
from .check import Check, NullCheck
from .test import Test, NullTest
from .deactivate import Deactivation, NullDeactivation
from .defaults import ACTIVATE, CHECK, TEST, DEACTIVATE

from smashlib.aliases import AliasMixin

class CommandLineMixin(object):
    def build_argparser(self):
        """ """
        parser = Reporter.build_argparser(self)
        parser.add_argument('-p', '--project', default='')
        return parser

    def parse_argv(self):
        args, unknown = Reporter.parse_argv(self)
        if args.project:
            # cannot effect the change here due to some race condition.
            # smash will send a signal when it's initialization is complete
            # and we just store a variable that the signal handler can use.
            self.use_project = args.project

        return args, unknown

    @receives_event(C_DOT_CMD)
    def consider_dot_cmd(self, line):
        tmp = line.split()
        cmd, args = tmp.pop(0), tmp
        cmd = getattr(self.interface, '_'+cmd, None)
        if cmd:
            if not callable(cmd):
                print cmd
            else:
                self.report("found command: {0}".format(cmd))
                cmd(*args)

    @receives_event(C_SMASH_INIT_COMPLETE)
    def use_requested_project(self):
        try:
            #self.activate_project(args.project)
            getattr(self.interface, self.use_project)
            self.use_project = None
        except UnknownProjectError:
            msg = 'unknown project: {0}'.format(self.use_project)
            self.warning(msg)
        except AttributeError:
            pass

class ProjectManager(CommandLineMixin, AliasMixin, Reporter):
    """ """
    search_dirs      = EventfulList(default_value=[], config=True)
    project_map      = EventfulDict(default_value={}, config=True)
    alias_map        = EventfulDict(default_value={}, config=True)
    activation_map   = EventfulDict(default_value={}, config=True)
    check_map        = EventfulDict(default_value={}, config=True)
    test_map         = EventfulDict(default_value={}, config=True)
    deactivation_map = EventfulDict(default_value={}, config=True)
    venv_map         = EventfulDict(default_value={}, config=True)
    alias_map        = EventfulDict(default_value={}, config=True)
    macro_map        = EventfulDict(default_value={}, config=True)

    _current_project = None


    def init(self):
        # at this point project_map has been created from
        # configuration data, but it's callback mechanism
        # which does validation has not be registered yet.
        # bind it, then reinitialize project_map to fix
        # up and then bind any data set so far
        self.project_map.on_set(self._event_set_project_map)
        for x in self.project_map.copy():
            self.project_map[x]=self.project_map[x]
        self._load_alias_group('__smash__')

    def init_interface(self, pmi):
        ProjectManagerInterface._project_manager = self
        self.smash.shell.user_ns['proj'] = pmi

    def init_magics(self):
        ProjectMagics.project_manager = self
        self.smash.shell.register_magics(ProjectMagics)

    @property
    def _project_name(self):
        return self._current_project

    @property
    def _project_dir(self):
        return self.project_map[self._project_name]

    @property
    def reverse_project_map(self):
        return dict([[v,k] for k,v in self.project_map.items()])

    @receives_event(C_CHANGE_DIR, quiet=True)
    def show_project_help(self, new_dir, old_dir):
        if new_dir in self.project_map.values():
            project_name = self.reverse_project_map[new_dir]
            _help = 'this directory is a project.  to activate it, type {0}'
            _help = _help.format(green('proj.'+project_name))
            #self.info(_help)

    def _event_set_project_map(self, key, val):
        """ final word in cleaning/verifying/binding
            input that goes to project_map.  project_map
            should have only pristine data. Therefore DO
            NOT abstract the helper method "_bind_project".
        """
        def _bind_project(name, path):
            """ NOTE: be aware this is also used for re-binding """
            if not ope(path):
                self.report("bound project {0} to nonexistent {1}".format(
                    name, path))
            self.update_interface()
        name = key
        clean_name = clean_project_name(name)
        clean_path = abspath(expanduser(val))
        dict.__setitem__(
            self.project_map,
            clean_name,
            clean_path)
        _bind_project(clean_name, clean_path)


    def _event_set_search_dirs(self, slice_or_index, base_dir):
        if isinstance(slice_or_index, slice):
            assert isinstance(base_dir, list) #refresh, ie rehashx
            self.refresh()
            return
        base_dir = os.path.abspath(os.path.expanduser(base_dir))
        #if base_dir in self.search_dirs:
        if not os.path.exists(base_dir):
            msg = "new search_dir doesnt exist: {0}"
            self.warning(msg.format(base_dir))
            return
        else:
            self._bind_one(base_dir)

    #@receives_event(C_REHASH_EVENT)
    #def refresh(self, none):
    #    # TODO: deprecate
    #    [ self._bind_one(x) for x in set(self.search_dirs)]

    def _bind_one(self, base_dir):
            base_dir = os.path.abspath(os.path.expanduser(base_dir))
            contents = os.listdir(unicode(base_dir))
            bind_list = []
            for name in contents:
                if name.startswith('.'):
                    self.warning("skipping "+name)
                path = os.path.join(base_dir, name)
                #raise Exception,path
                self.project_map[name] = path
            self.report("discovered {0} projects under '{1}'".format(
                len(bind_list), base_dir))
            self.update_interface()

    def update_interface(self):
        """ so that tab-completion works on any bound projects, the
            properties on ProjectManagerInterface (aka user_ns['proj'])
            will be updated
        """
        def _get_prop(name, path):
            def fxn(himself):
                self.activate_project(name)
            out = property(fxn)
            return out
        for name, path in self.project_map.items():
            prop = _get_prop(name, path)
            setattr(ProjectManagerInterface, name, prop)

    def _require_project(self, name):
        if name not in self.project_map:
            raise UnknownProjectError(name)

    def jump_project(self, name):
        self._require_project(name)
        _dir = os.path.expanduser(self.project_map[name])
        if not os.path.exists(_dir):
            self.report("Not found: {0}".format(_dir))
        else:
            self.shell.magic('pushd {0}'.format(_dir))

    def _guess_deactivation_steps(self, name, dir):
        operation_dict = DEACTIVATE
        return self._guess_operation_steps(
            name, dir, operation_dict,
            Deactivation, NullDeactivation)

    def _guess_activation_steps(self, name, dir):
        operation_dict = ACTIVATE
        return self._guess_operation_steps(
            name, dir, operation_dict,
            Activation, NullActivation)

    def _guess_check_steps(self, name, dir):
        operation_dict = CHECK
        return self._guess_operation_steps(
            name, dir, operation_dict,
            Check, NullCheck)

    def _guess_test_steps(self, name, dir):
        operation_dict = TEST
        return self._guess_operation_steps(
            name, dir, operation_dict,
            Test, NullTest)

    def _guess_operation_steps(
        self, name, dir, operation_dict,
        step_kls, default_step):
        assert all([inspect.isclass(step_kls),
                    inspect.isclass(default_step),
                    issubclass(step_kls,OperationStep),
                    issubclass(default_step,NullOperationStep)])
        steps = []
        ptype = self.guess_project_type(name)

        for subtype in ptype:
            these_steps = operation_dict.get(subtype, [])
            steps += [
                step_kls(
                    subtype, pm=self,
                    fxn=fxn, args=(self,)) \
                for fxn in these_steps]
        if not steps:
            steps.append(default_step(self))
        return steps

    def perform_operation(self, name, op_name):
        self.report("{0}: {1}".format(op_name,name))
        self._require_project(name)
        _dir = self.project_map[name]
        step_guesser = getattr(self, '_guess_{0}_steps'.format(op_name))
        default = step_guesser(name, _dir)
        op_steps = getattr(self, '{0}_map'.format(op_name)).get(name, default)
        results=[]
        for fxn in op_steps:
            results.append([fxn, fxn()])
            if not op_steps.index(fxn)==len(op_steps)-1:
                console.draw_line()
        self.publish('post_operation', op_name, name)
        return dict(results)

    @receives_event('post_operation')
    def handle_post_op(self, op_name, project_name):
        if op_name=='activation':
            self._load_alias_group(project_name)
        if op_name=='deactivation':
            self._unload_alias_group(project_name)

    def deactivate(self):
        name = self._current_project
        if name is None:
            return
        self.perform_operation(name, 'deactivation')
        self._current_project = None

    def activate_project(self, name):
        self.deactivate()
        self._current_project = name
        self.perform_operation(name, 'activation')
        if not getcwd() == self.project_map[name]:
            self.jump_project(name)
    activate = activate_project

    def test(self, name):
        self.perform_operation(name, 'test')

    def check(self, pname):
        return self.perform_operation(pname, 'check')

    def guess_project_type(self, project_name):
        pdir = self.project_map[project_name]
        return guess_dir_type(pdir)
