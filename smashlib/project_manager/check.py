""" smashlib.project_manager.check
"""

from smashlib.util.linter import PyLinter, HaskellLinter
from .operation import OperationStep, NullOperationStep


class Check(OperationStep):
    operation_name = 'check'


class NullCheck(NullOperationStep):
    operation_name = 'check'

def python_lint(project_manager):
    """ """
    return _get_linter(PyLinter, project_manager)

def haskell_lint(project_manager):
    """ """
    return _get_linter(HaskellLinter, project_manager)

def _get_linter(LinterClass, project_manager):
    """ """
    project_name = project_manager._current_project
    if project_name is None:
        project_manager.report("No project has been selected.")
        return
    pdir = project_manager.project_map[project_name]
    linter = LinterClass(project_manager.smash.shell.config,
                         cmd_exec=project_manager.smash.system,)
    return linter(pdir)
