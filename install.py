#!/usr/bin/env python
""" install.py for SmaSh
"""

import os
from setuptools import setup as _setup
from setuptools.command.install import install

try:
    import goulash
except ImportError:
    err = ('Smash-shell installer requires goulash.  '
           '"pip install goulash==0.2" and try again')
    raise SystemExit(err)
try:
    import fabric
except ImportError:
    err = ('Smash-shell installer requires fabric.  '
           '"pip install goulash==1.10.0" and try again')
    raise SystemExit(err)

from fabric.colors import red
from fabric import api as fab_api
from goulash.venv import is_venv, to_vbin

DOT_SMASH = os.path.abspath(os.path.expanduser('~/.smash'))
IPY_VERSION = '3.0.0-dev'
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
            self.fab_api.local('virtualenv --no-site-packages '+DOT_SMASH)

    def venv_ipython(self):
        venv_ipython = os.path.join(DOT_SMASH, 'bin', 'ipython')
        with fab_api.quiet():
            result =  fab_api.local(
                '{0} --version'.format(venv_ipython),
                capture=True)
        return result

    def add_ipython(self):
        self.report("smash requires dev version of ipython.  looking for it..")
        result = self.venv_ipython()
        have_ipy = result.succeeded
        good_IPY_VERSION = result.succeeded and (result.strip()==IPY_VERSION)
        if have_ipy:
            self.report("{0} has ipython..".format(DOT_SMASH))
            if good_IPY_VERSION:
                self.report(".. and the version is correct")
            else:
                msg = "..but the version is wrong. getting the correct version"
                self.report(msg)
                self.clone_ipython(IPY_VERSION)
        else:
            msg = "ipython not found.  getting the correct version"
            self.report(msg)
            self.clone_ipython(IPY_VERSION)

        if not good_IPY_VERSION:
            self.report("installing ipython into smash venv")
            if self.__class__==InstallCommand:
                cmd = "cd {0} && {1} setup.py install"
            elif self.__class__==DevelopCommand:
                cmd = "cd {0} && {1} setup.py develop"
            fab_api.local(cmd.format(
                os.path.join(DOT_SMASH,'ipython'),
                os.path.join(DOT_SMASH, 'bin','python')))

    def clone_ipython(self, version):
        url = 'http://github.com/ipython/ipython.git'
        #or..  https://github.com/ipython/ipython/archive/master.zip
        self.report("cloning the official repo.  this might take a while")
        self.report("clone url: "+url)
        ipy_clone_path = os.path.join(DOT_SMASH, 'ipython')
        if not os.path.exists(ipy_clone_path):
            with fab_api.settings(warn_only=True):
                cmd = ('cd {0} && '
                       'git clone --branch master '
                       '--single-branch --depth 1 {1}')
                result = fab_api.local(
                    cmd.format(DOT_SMASH, url),
                    capture=True)
            if not result.succeeded:
                print result
                err = 'failed to clone.  check your network connection?'
                self.report(err)
                raise SystemExit()
        else:
            self.report('official repo is already already cloned..')
            self.report('.. will not update it')

    def report(self,msg):
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
        if self.__class__==InstallCommand:
            cmd = '{0} {1} install'.format(python, SMASH_SETUP_PY)
        elif self.__class__==DevelopCommand:
            cmd = '{0} {1} develop'.format(python, SMASH_SETUP_PY)


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
        self.add_ipython()
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
