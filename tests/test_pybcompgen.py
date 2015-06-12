""" tests/test_pybcompgen.py
"""
import unittest
from smashlib.bin.pybcompgen import complete

class TestFabric(unittest.TestCase):

    def test_pybcompgen(self):
        results = complete('whi')
        self.assertTrue('which' in results)

if __name__=='__main__':
    unittest.main()
