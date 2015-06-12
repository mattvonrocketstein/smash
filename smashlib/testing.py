""" smashlib.testing

    Base classes, etc for smashlib's tests.

    Note: The tests themselves are in the source
          root, not inside the smashlib package
"""
import unittest
from smashlib.import_hooks import hijack_ipython_module
hijack_ipython_module()

main = unittest.main

class TestCase(unittest.TestCase):
    pass
