""" smashlib.project_manager.deactivate
"""
from .operation import OperationStep, NullOperationStep

class Deactivation(OperationStep):
    pass

class NullDeactivation(NullOperationStep):
    pass

def deactivate_python_venv(pm):
    pm.shell.magic('venv_deactivate')

def deactivate_vagrant_project(pm):
    pm.smash.system('vagrant halt')
