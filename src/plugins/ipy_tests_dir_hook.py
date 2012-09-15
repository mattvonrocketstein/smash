""" ipy_tests_dir_hook
"""
import os

from smash.util import report, post_hook_for_magic
from smash.python import only_py_files, opj, ope, glob


class TestsMenu(object):
    @property
    def __doc__(self):
        out = repr(self)+'\n'
        for f in self.files:
            out += ' {0}: {1}\n'.format(self.files.index(f), f)
        out+="""

HINT: You can run the tests above by using commands like ",tests.run 1"
        """
        return out

    def __repr__(self):
        return '<Tests @ "{0}">'.format(self.base)

    def run(self, i):
        i = int(i)
        f = self.files[i]
        cmd = 'pytest -v {0}'.format(f)
        __IPYTHON__.runlines(cmd)

    def __init__(self, base, abs_test_files):
        self.base = base
        self.files = abs_test_files

def look_for_tests():
    wd    = os.getcwd()
    files = os.listdir(wd)
    tdir  = opj(wd, 'tests')
    if ope(tdir) and os.path.isdir(tdir):
        report.tests_magic('Discovered test-dir: {red}' + tdir + '{normal}')
        abs_test_files = glob( opj(tdir, 'test_*.py') )
        rel_test_files = [ x[ len(wd) + 1 : ] for x in abs_test_files ]
        report.tests_magic(str(rel_test_files) + '\n')
        tests = TestsMenu(tdir, abs_test_files)
        if all(['tests' in __IPYTHON__.user_ns,
                not isinstance(__IPYTHON__.user_ns.get('tests',None), TestsMenu)]):
            report.tests_magic('(oops, "tests" name is already taken.  erring on the side of caution)')
        else:
            __IPYTHON__.user_ns.update(tests=tests)
            report.tests_magic('updated tests magic.  type "tests?" for help')

    if 'tests.py' in files:
        print 'Discovered test file.'

if __name__=='__smash__':
    post_hook_for_magic('cd', look_for_tests)
