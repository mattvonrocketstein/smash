""" smashlib.project_manager.magics
"""
from IPython.core.magic import Magics, magics_class, line_magic

@magics_class
class ProjectMagics(Magics):
    def _run_op(self, op_name, parameter_s):
        parameter_s = parameter_s or self.project_manager._current_project
        if parameter_s:
            op=getattr(self.project_manager,op_name)
            op(parameter_s)

    @line_magic
    def project_ack(self, parameter_s):
        return self.project_manager._ack(parameter_s)

    @line_magic
    def activate_project(self, parameter_s=''):
        self._run_op('activate', parameter_s)

    @line_magic
    def add_project(self, parameter_s=''):
        parameter_s = parameter_s or self.project_manager._current_project
        if parameter_s:
            name = parameter_s.split()[0]
            path = parameter_s[len(name)+1:]
            self.project_manager.project_map[name]=path

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
