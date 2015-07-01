""" smashlib.project_manager.activate
"""

from goulash.venv import contains_venv
from goulash._os import summarize_fpath
from goulash._fabric import require_bin, MissingSystemCommand

from .operation import OperationStep, NullOperationStep


class Activation(OperationStep):
    pass


class NullActivation(NullOperationStep):
    pass


def activate_python_venv(project_manager):
    """ if any venv's are found, activate the first """
    name = project_manager._current_project
    _dir = project_manager.project_map[name]
    found_venv = None
    default_venv_dir = project_manager.venv_map.get(name, None)
    if default_venv_dir:
        default_venv = contains_venv(
            default_venv_dir,
            report=project_manager.report,
            # typically ignoring tox is a good idea.  but maybe
            # someone wants to specifically use the tox dir?
            # ignore_dirs='.tox'
        )
        if not default_venv:
            msg = ("ProjectManager.venv_map uses {0}, "
                   "but no venv was found")
            msg = msg.format(default_venv_dir)
            project_manager.warning(msg)
        else:
            found_venv = default_venv
            project_manager.report("venv_map specifies to use {0}".format(
                summarize_fpath(found_venv)))
    else:
        found_venv = contains_venv(
            _dir, report=project_manager.report,
            ignore_dirs=['.tox'],
        )

    if found_venv:
        project_manager.shell.magic('venv_activate {0}'.format(found_venv))


def activate_vagrant(pm):
    try:
        require_bin('vagrant')
    except MissingSystemCommand, e:
        pm.warning("{0}: cannot execute activate_vagrant".format(e))
    else:
        pm.smash.system('vagrant list')
