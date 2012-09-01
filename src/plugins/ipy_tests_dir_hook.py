""" ipy_tests_dir_hook
"""
import os

from smash.util import post_hook_for_magic
from smash.python import only_py_files, opj, glob

def look_for_tests():
    wd    = os.getcwd()
    files = os.listdir(wd)
    if 'tests' in files and os.path.isdir(opj(wd, 'tests')):
        print 'Discovered test-dir.'
        pyfiles = glob(wd, 'tests','test_*.py')
        print pyfiles
    if 'tests.py' in files:
        print 'Discovered test file.'

if __name__=='__smash__':
    post_hook_for_magic('cd', look_for_tests)
