"""
"""
from .operation import OperationStep, NullOperationStep

class Test(OperationStep):
    operation_name = 'test'


class NullTest(NullOperationStep):
    operation_name = 'test'

def python_test(project_manager):
    """ if any venv's are found, check the first """
    pm = project_manager
    project_name = project_manager._current_project
    if project_name is None:
        pm.report("No project has been selected.")
        return
    #pdir = project_manager.project_map[project_name]
    pm.report("python_test niy")
