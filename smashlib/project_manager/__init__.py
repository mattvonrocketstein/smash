""" smashlib.project_manager
"""
import os
import inspect
from IPython.utils.traitlets import EventfulDict, EventfulList

from goulash.venv import find_venvs

from smashlib.ipy_cd_hooks import CD_EVENT
from smashlib.project_manager.util import (
    clean_project_name, UnknownProjectError)
from smashlib.python import abspath, expanduser
from smashlib.util import guess_dir_type
from smashlib.util.events import receives_event
from smashlib.util.ipy import green
from smashlib.v2 import Reporter

from .operation import OperationStep,NullOperationStep
from .activate import Activation, NullActivation
from .check import Check, NullCheck, python_flakes
from .activate import activate_vagrant, activate_python_venv
from .deactivate import Deactivation, NullDeactivation
from .deactivate import deactivate_python_venv

ACTIVATE = dict(
    python=[activate_python_venv],
    vagrant=[activate_vagrant],
    )

CHECK = dict(
    python=[python_flakes])

TEST = dict(
    python=[python_flakes])

DEACTIVATE = dict(
    python=[deactivate_python_venv])

class ProjectManager(Reporter):
    search_dirs      = EventfulList(default_value=[], config=True)
    project_map      = EventfulDict(default_value={}, config=True)
    alias_map        = EventfulDict(default_value={}, config=True)
    activation_map   = EventfulDict(default_value={}, config=True)
    check_map        = EventfulDict(default_value={}, config=True)
    deactivation_map = EventfulDict(default_value={}, config=True)
    venv_map         = EventfulDict(default_value={}, config=True)

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

    def init_pmi(self, pmi):
        ProjectManagerInterface._project_manager = self
        self.smash.shell.user_ns['proj'] = pmi

    def init_magics(self):
        from smashlib.project_manager.magics import ProjectMagics
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

    @receives_event(CD_EVENT)
    def cd_hook(self, new_dir, old_dir):
        if new_dir in self.project_map.values():
            project_name = self.reverse_project_map[new_dir]
            _help='this directory is a project.  to activate it, type {0}'
            _help = _help.format(green('proj.'+project_name))
            self.info(_help)

    def _event_set_project_map(self, key, val):
        """ final word in cleaning/verifying/binding
            input that goes to project_map.  project_map
            should have only pristine data. Therefore DO
            NOT abstract the helper method "_bind_project".
        """
        def _bind_project(name, path):
            """ NOTE: be aware this is also used for re-binding """
            if not os.path.exists(path):
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
        base_dir = os.path.abspath(os.path.expanduser(base_dir))
        if not os.path.exists(base_dir):
            msg = "new search_dir doesnt exist: {0}"
            self.warning(msg.format(base_dir))
        else:
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

    def build_argparser(self):
        parser = super(ProjectManager, self).build_argparser()
        parser.add_argument('-p','--project', default='')
        return parser

    def parse_argv(self):
        args, unknown = super(ProjectManager,self).parse_argv()
        if args.project:
            try:
                self.activate_project(args.project)
            except UnknownProjectError:
                msg = 'unknown project: {0}'.format(args.project)
                self.warning(msg)
        return args, unknown

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

    def deactivate(self):
        name = self._current_project
        if name is None:
            return
        self.perform_operation(name, 'deactivation')
        self._current_project = None

    def perform_operation(self, name, op_name):
        self.report("{0}: {1}".format(op_name,name))
        self._require_project(name)
        _dir = self.project_map[name]
        step_guesser = getattr(self, '_guess_{0}_steps'.format(op_name))
        default = step_guesser(name, _dir)
        op_steps = getattr(self,'{0}_map'.format(op_name)).get(name, default)
        results = [fxn() for fxn in op_steps]
        return results

    def activate_project(self, name):
        self.deactivate()
        self._current_project = name
        self.perform_operation(name, 'activation')
        if not os.getcwd() == self.project_map[name]:
            self.jump_project(name)
    activate = activate_project

    def test(self, name):
        self.perform_operation(name, 'test')

    def guess_project_type(self, project_name):
        pdir = self.project_map[project_name]
        return guess_dir_type(pdir)

    def check(self, pname):
        return self.perform_operation(pname, 'check')


class ProjectManagerInterface(object):
    """ This object should be a singleton and will be assigned to
        that main namespace as "proj".  In addition to the methods
        you see below, The ProjectManager extension
        will dynamically add/remove properties on to this
    """
    _project_manager = None

    @property
    def _type(self):
        return self._project_manager.guess_project_type(
            self._project_manager._current_project)

    @property
    def _venvs(self):
        pname = self._project_manager._current_project
        return find_venvs(
            self._project_manager.project_map[pname])

    @property
    def _recent(self):
        """ return a list of the top 10 most recently changed files in the
            current project's directory, where list[0] was changed most
            recently.  this automatically takes into account ignoring dotfiles
            and .gitignore contents.
        """
        gitignore = os.path.join(
            self._project_manager._project_dir,
            '.gitignore')
        from smashlib.python import ope
        patterns = ['*/.*/*']
        if ope(gitignore):
            with open(gitignore) as fhandle:
                patterns += [x.strip() for x in fhandle.readlines()]
        patterns = ' -and '.join( ['! -wholename "{0}"'.format(p) \
                                   for p in patterns ] )
        if patterns:
            patterns = '\\( {0} \\)'.format(patterns)
        # find . -type f \( -iname "*.c" -or -iname "*.asm" \)
        sed = """| sed 's/[^[:space:]]\+ //';"""
        base_find = 'find {0} -type f {1}'.format(
            self._project_manager._project_dir, patterns)
        cmd = '{0} -printf "%T+ %p\n" | sort -n {1}'.format(base_find, sed)
        filenames = self._project_manager.smash.system(cmd, quiet=True)
        filenames = filenames.split('\n')
        filenames.reverse()
        return filenames[:10]

    def _ack(self, pat):
        """ TODO: should really be some kind of magic """
        from smashlib.util._fabric import require_bin
        require_bin('ack-grep')
        venvs = self._venvs
        cmd = 'ack-grep "{0}" "{1}" {2}'
        pdir = self._project_manager.project_map[
            self._project_manager._current_project]
        ignores = ['--ignore-dir="{0}"'.format(venv) for venv in venvs]
        ignores = ' '.join(ignores)
        cmd = cmd.format(pat, pdir, ignores)
        results = self._project_manager.smash.system(cmd)
        print results

    @property
    def _check(self):
        pm = self._project_manager
        project_name = pm._current_project
        pm.check(project_name)
