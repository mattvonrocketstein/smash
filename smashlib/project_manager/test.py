"""
"""
from smashlib.util.linter import PyLinter
from .operation import OperationStep, NullOperationStep

class Test(OperationStep):
    operation_name = 'test'


class NullTest(NullOperationStep):
    operation_name = 'test'
