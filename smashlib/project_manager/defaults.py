""" smashlib.project_manager.defaults

    Maps for project-types -> operation
"""

from .deactivate import deactivate_python_venv
from .activate import activate_vagrant, activate_python_venv
from .check import python_lint, haskell_lint, puppet_lint
from .test import python_test

ACTIVATE = dict(
    python=[activate_python_venv],
    vagrant=[activate_vagrant],
    )

CHECK = dict(
    python=[python_lint],
    haskell=[haskell_lint],
    puppet=[puppet_lint],
    )

TEST = dict(
    python=[python_test])

DEACTIVATE = dict(
    python=[deactivate_python_venv])
