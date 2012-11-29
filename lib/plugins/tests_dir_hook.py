""" tests_dir_hook
"""
import os

from smashlib.plugins import SmashPlugin
from smashlib.util import report, post_hook_for_magic
from smashlib.python import only_py_files, opj, ope, glob, getcwd


class TestsMenu(object):

    @property
    def __doc__(self):
        # FIXME: do this with a thread so there's no waiting
        out = repr(self) + '\n'
        for f in self.files:
            out += ' {0}: {1}\n'.format(self.files.index(f), f)
        out += """\n\nHINT: You can run the tests above by using commands like ",tests.run 1"\n"""
        return out

    def __repr__(self):
        return '<Tests @ "{0}">'.format(self.base)

    def run(self, i):
        i = int(i)
        f = self.files[i]
        cmd = 'pytest --capture=no -v {0}'.format(f)
        __IPYTHON__.runlines(cmd)

    def __init__(self, base, abs_test_files):
        self.base = base
        self.files = abs_test_files

class TestsHook(object):
    """ FIXME?:  this wont trigger if you 'cd myproject/tests' """
    requires = ['pytest']
    report = report.tests_magic

    def handle_python_testdir(self, tdir):
        wd = getcwd()
        abs_test_files = glob( opj(tdir, 'test_*.py') )
        self.report('Discovered test-dir@"{0}" -- ({1} files)'.format(tdir, len(abs_test_files)))
        rel_test_files = [ x[ len(wd) + 1 : ] for x in abs_test_files ]
        self.report(str(rel_test_files))
        tests = TestsMenu(tdir, abs_test_files)
        if all(['tests' in __IPYTHON__.user_ns,
                not isinstance(__IPYTHON__.user_ns.get('tests',None), TestsMenu)]):
            self.report('(oops, "tests" name is already taken.  erring on the side of caution)')
        else:
            __IPYTHON__.user_ns.update(tests=tests)
            self.report('updated tests magic.  type "tests?" for help')

    def handle_python_testfile(self, wd):
        tfile = opj(wd, 'tests.py')
        self.report('Discovered test file: '+tfile)
        self.report("niy")

    def __call__(self):
        wd    = getcwd()
        if os.path.split(wd)[-1] == 'tests':
            return self.handle_python_testdir(wd)
        files = os.listdir(wd)
        tdir  = opj(wd, 'tests')
        if ope(tdir) and os.path.isdir(tdir):
            self.handle_python_testdir(tdir)
        elif 'tests.py' in files:
            self.handle_python_testfile(wd)

class Plugin(SmashPlugin):
    def install(self):
        post_hook_for_magic('cd', TestsHook())
