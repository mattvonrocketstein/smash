""" tests_dir_hook
"""
import os

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import post_hook_for_magic, ope, opj, report_if_verbose
from smashlib.python import only_py_files, opj, ope, glob, getcwd
from smashlib.venv import venv_bin
from smashlib.util import report as default_report


TEST_PROG      = 'py.test'
TEST_PROG_ARGS = ['-s', '-v']
SMASH_CMD_NAME = 'tests'

report = default_report.smash_tests

def test_prog():
    local_tester = venv_bin(TEST_PROG)
    if ope(local_tester):
        #report_if_verbose("found {0} in venv: {1}".format(TEST_PROG,local_tester))
        return local_tester
    else:
        #report_if_verbose("didnt find {0} in venv: {1}".format(TEST_PROG, local_tester))
        return TEST_PROG

def test_cmd(fname_or_dir):
    return '{0} {1} {2}'.format(
        test_prog(), ' '.join(TEST_PROG_ARGS), fname_or_dir)

class TestsMenu(object):

    def __qmark__(self):
        # FIXME: do this with a thread so there's no waiting
        out = repr(self) + '\n'
        for f in self.files:
            out += ' {0}: {1}\n'.format(self.files.index(f), f)
        out += ('\n\n'
                'HINT: You can run the tests by using commands like: '
                ' ",tests 1" or ",tests all"'
                '\n')
        report(out)

    def __repr__(self):
        return '<Tests @ "{0}">'.format(self.base)

    def run(self, i, recursive=False):
        if i=='all':
            for x in range(len(self.files)):
                self.run(x, recursive=True)
        else:
            i = int(i)
            try:
                f = self.files[i]
            except IndexError:
                report('No such test!')
                return
            cmd = test_cmd(f)
            report('running "{0}"'.format(cmd))
            __IPYTHON__.runlines(cmd)
        if not recursive:
            report("HINT: you might find some useful information using 'tests.summary?'")
    __call__ = run

    def __init__(self, base, abs_test_files):
        self.base = base
        self.files = abs_test_files

class DefaultTestsMenu(TestsMenu):
    maxdepth = 5

    def __init__(self):
        super(DefaultTestsMenu, self).__init__('not-set', [])

    def __qmark__(self):
        report('No tests have been discovered yet.')
        report('HINT: type "{0}.discover"'.format(SMASH_CMD_NAME))

    def __call__(self, *args, **kargs):
        self.__qmark__()
    run = __call__

    @property
    def discover(self):
        report("Looking for test-dirs (max-depth={0})".format(self.maxdepth))
        cmd    = 'find . -maxdepth {0} -type d -name tests'.format(self.maxdepth)
        result = [ x.strip() for x in os.popen(cmd).readlines() ]
        self._discover_cache = result
        if not result:
            report("No tests found.")
        else:
            report("Found {0} test-dirs.".format(len(result)))
            for fname in result:
                report("  {0}: {1}".format(
                    result.index(fname), fname))
            if len(result)==1:
                report("Only one candidate found for tests, "
                                   "setting it as default.")
                __IPYTHON__.runlines('cd '+result[0])
            else:
                report(' to set a directory, type ", tests <i>"')
                report("( NIY )")


    def __repr__(self):
        return '<Tests: none discovered.>'


class TestsHook(object):
    """ FIXME?:  this wont trigger if you 'cd myproject/tests' """

    def handle_python_testdir(self, tdir):
        wd = getcwd()
        abs_test_files = glob( opj(tdir, 'test_*.py') )
        report('Discovered test-dir@"{0}" -- ({1} files)'.format(
            tdir, len(abs_test_files)))
        rel_test_files = [ x[ len(wd) + 1 : ] for x in abs_test_files ]
        report(str(rel_test_files))
        tests = TestsMenu(tdir, abs_test_files)
        if all([SMASH_CMD_NAME in __IPYTHON__.user_ns,
                not isinstance(
                    __IPYTHON__.user_ns.get(SMASH_CMD_NAME, None),
                    TestsMenu)]):
            report('(oops, "tests" name is already taken.'
                        '  erring on the side of caution)')
        else:
            __IPYTHON__.user_ns.update(tests=tests)
            report('updated tests magic.  type "tests?" for help')

    def handle_python_testfile(self, wd):
        tfile = opj(wd, 'tests.py')
        report('Discovered test file: ' + tfile)
        report("niy")

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
        else:
            __IPYTHON__.user_ns.update(tests=DefaultTestsMenu())

class Plugin(SmashPlugin):

    requires = ['pytest']

    def install(self):
        post_hook_for_magic('cd', TestsHook())
        # "tests" should be in the namespace immediately after smash starts,
        # without the user changing-directory first.  in order for that to occur,
        # we need to run this once when the plugin is installed
        TestsHook()()
