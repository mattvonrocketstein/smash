"""
"""
import unittest
from smashlib.bin.pybcompgen import complete
class TestPybcompgen(unittest.TestCase):
    def test_env_var(self):
        cmd = 'echo $HOM'
        expected = ['$HOME']
        self.assertEqual(complete(cmd), expected)
    def test_git_subcommands(self):
        #pybcompgen "git lo"
        cmd = "git lo"
        expected=["log", "lol", "lola"]
        self.assertEqual(complete(cmd),expected)


if __name__=='__main__':
    unittest.main()
