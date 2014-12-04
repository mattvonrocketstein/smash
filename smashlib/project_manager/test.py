"""
"""
from smashlib import get_smash
from smashlib.util._tox import has_tox
from .operation import OperationStep, NullOperationStep, require_active_project


class Test(OperationStep):
    operation_name = 'test'


class NullTest(NullOperationStep):
    operation_name = 'test'


@require_active_project
def python_test(project_manager):
    """ simply run tox if tox.ini is found.

        TODO: the "otherwise" part is hard if tox isn't present, but,
              eventually a reasonable heuristic can be defined.  special
              treatment should probably be given to django since it's so
              popular and the testing procedure is pretty idiosyncratic.
    """
    pm = project_manager
    pname = project_manager._current_project
    pdir = project_manager.project_map[pname]
    if has_tox(pdir):
        project_manager.report("detected tox.  running it")
        get_ipython().system_raw('tox')
    project_manager.report("not implemented yet")
