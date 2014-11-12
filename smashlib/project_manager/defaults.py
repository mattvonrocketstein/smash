""" smashlib.project_manager.defaults
"""

from .deactivate import deactivate_python_venv
from .activate import activate_vagrant, activate_python_venv
from .check import python_flakes

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
