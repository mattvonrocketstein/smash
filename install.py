#!/usr/bin/env python
""" install.py for SmaSh
"""

import os
from setuptools import setup as _setup
from setuptools.command.install import install

try:
    import goulash.version
    print 'goulash', goulash.version.__version__
except ImportError:
    err = ('Smash-shell installer requires goulash.  '
           '"pip install goulash==0.5" and try again')
    raise SystemExit(err)
try:
    import fabric.version
    print 'fabric',fabric.version.__version__
except ImportError:
    err = ('Smash-shell installer requires fabric.  '
           '"pip install goulash==1.10.0" and try again')
    raise SystemExit(err)

from fabric.colors import red
from fabric import api as fab_api
from goulash.venv import is_venv, to_vbin

DOT_SMASH = os.path.abspath(os.path.expanduser('~/.smash'))

SMASH_SETUP_PY = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    'setup.py'))
SMASH_REQS = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    'requirements.txt'))

class InstallCommand(install):

    def build_smash_venv(self):
        if is_venv(DOT_SMASH):
            self.report("{0} is already a venv.  leaving it alone".format(
                DOT_SMASH))
        else:
            self.report("creating smash venv")
            fab_api.local('virtualenv --no-site-packages '+DOT_SMASH)

    def report(self, msg):
        red(msg)

    def _require_bin(self, name, deb_pkg_name=None):
        with fab_api.quiet():
            result =  fab_api.local('which "{0}"'.format(name))
        if not result.succeeded:
            err=("Smash shell installer requires {0}.".format(name))
            self.report(err)
            if deb_pkg_name:
                print ("To continue, run 'apt-get install {0}'"
                       " and try again.").format(deb_pkg_name)
            raise SystemExit(err)

    def add_smashlib_reqs(self):
        pip = self.smash_pip
        cmd = '{0} install -r {1}'.format(pip, SMASH_REQS)
        fab_api.local(cmd)
        self.report("finished installing {0} to {1}".format(
            SMASH_REQS, DOT_SMASH))

    def add_smashlib(self):
        python = self.smash_python
        self.add_smashlib_reqs()
        this_dir = os.path.dirname(__file__)
        if self.__class__==InstallCommand:
            cmd = 'cd {0} && {1} {2} install'.format(
                this_dir, python, SMASH_SETUP_PY)
        elif self.__class__==DevelopCommand:
            cmd = 'cd {0} && {1} {2} develop'.format(
                this_dir, python, SMASH_SETUP_PY)


        fab_api.local(cmd)
        self.report("finished install smashlib to {0}".format(
            DOT_SMASH))
        self.add_symlink()

    def add_symlink(self):
        smash_shell = os.path.join(self.smash_vbin, 'run_smash')
        self.report("adding symlink to ")
        _ubin = os.path.expanduser('~/bin')
        if not os.path.exists(_ubin):
            self.report("~/bin not found, creating it")
            os.mkdir(_ubin)
        fab_api.local('ln -nfs {0} {1}'.format(
                     smash_shell,
                     os.path.join(_ubin,'smash')))

    @property
    def smash_pip(self):
        return os.path.join(self.smash_vbin, 'pip')

    @property
    def smash_python(self):
        return os.path.join(self.smash_vbin, 'python')

    @property
    def smash_vbin(self):
        vbin = to_vbin(DOT_SMASH)
        return vbin

    def run(self):
        self._require_bin('virtualenv', 'python-virtualenv')
        self._require_bin('git', 'git-core')
        self.build_smash_venv()
        self.add_smashlib()

class DevelopCommand(InstallCommand):
    pass

setup = lambda: _setup(
    name         = 'smash',
    author       = 'mattvonrocketstein',
    author_email = '$author@gmail',
    version      = '0.1',
    description  = 'SmaSh: a smart(er) shell',
    url          = 'http://github.com/mattvonrocketstein/smashlib',
    license      = 'MIT',
    keywords     = 'system shell bash pysh',
    platforms    = 'any',
    zip_safe     = False,
    cmdclass = {
        'install': InstallCommand,
        'develop': DevelopCommand,
        },
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 000 - Experimental',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent', ],
    )

if __name__=='__main__':
    import sys
    if not sys.argv[1:]:
        sys.argv.append('develop')
    usage_help = 'usage: install.py [install|develop|<nothing>]'
    if len(sys.argv)!=2:
        raise SystemExit(usage_help)
    if sys.argv[-1] not in ['install','develop']:
        raise SystemExit(usage_help)
    setup()
