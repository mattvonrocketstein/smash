""" smashlib.project_manager.check
"""
from goulash.venv import contains_venv
from goulash.util import summarize_fpath

from .operation import OperationStep, NullOperationStep


class Check(OperationStep):
    operation_name = 'check'


class NullCheck(NullOperationStep):
    operation_name = 'check'


def python_flakes(project_manager):
    """ if any venv's are found, check the first """
    pm = project_manager
    project_name = project_manager._current_project
    if project_name is None:
        pm.report("No project has been selected.")
        return
    pdir = project_manager.project_map[project_name]
    from smashlib.util.linter import PyLinter
    cmd_exec = project_manager.smash.system
    linter = PyLinter(project_manager.smash.shell.config,
                      cmd_exec=project_manager.smash.system,)
    #project_manager.shell.configurables.append(linter)
    return linter(pdir)
