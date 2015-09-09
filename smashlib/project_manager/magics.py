""" smashlib.project_manager.magics
"""
from report import report
from IPython.core.magic import Magics, magics_class, line_magic


@magics_class
class ProjectMagics(Magics):

    def _run_op(self, op_name, parameter_s):
        parameter_s = parameter_s or self.project_manager._current_project
        if parameter_s:
            op = getattr(self.project_manager, op_name)
            op(parameter_s)

    @line_magic
    def search(self, parameter_s):
        return 'niy'
        #self.project_manager.interface._ack(parameter_s)
    search_project = search

    @line_magic
    def activate_project(self, parameter_s=''):
        self._run_op('activate', parameter_s)

    @line_magic
    def add_project(self, parameter_s=''):
        parameter_s = parameter_s or self.project_manager._current_project
        if parameter_s:
            name = parameter_s.split()[0]
            path = parameter_s[len(name) + 1:]
            self.project_manager.project_map[name] = path

    @line_magic
    def env(self, parameter_s):
        # original: ipython.core.magics.osm.OSMagics.env
        from IPython.core.magics.osm import OSMagics
        all_env = OSMagics().env(parameter_s)
        all_env.pop('LS_COLORS', None) # large and annoying, never useful
        report("All environment variables: ", all_env)
        pname = self.project_manager._current_project
        if pname:
            project_local_env = self.project_manager.local_env
            report("This project: ", project_local_env)

        #if not parameter_s:


    @line_magic
    def check_project(self, parameter_s=''):
        self._run_op('check', parameter_s)

    @line_magic
    def build_project(self, parameter_s=''):
        self._run_op('build', parameter_s)

    @line_magic
    def test_project(self, parameter_s=''):
        self._run_op('test', parameter_s)

    @line_magic
    def jump(self, parameter_s=''):
        self.project_manager.jump_project(parameter_s)
