""" smashlib.project_manager.defaults
"""

from .deactivate import deactivate_python_venv
from .activate import activate_vagrant, activate_python_venv
from .check import python_flakes
from .test import python_test

ACTIVATE = dict(
    python=[activate_python_venv],
    vagrant=[activate_vagrant],
    )

CHECK = dict(
    python=[python_flakes])

TEST = dict(
    python=[python_test])

DEACTIVATE = dict(
    python=[deactivate_python_venv])
