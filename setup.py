import os
import sys
from glob import glob
from distutils.command.install_data import install_data as _install_data
from distutils.command.install import install as _install
from distutils.core import setup
from os.path import expanduser
from distutils.file_util import copy_file

ope = os.path.exists
opj = os.path.join
opd = os.path.dirname
opil = os.path.islink
ops = os.path.split
HOME_BIN = expanduser('~/bin')
HOME_IPY = os.path.expanduser('~/.ipython')

SMASH_INSTALLATION_HOME = opj(HOME_IPY, 'smash')
SMASH_LIB_DST_DIR = opj(SMASH_INSTALLATION_HOME, 'smash')
SMASH_PLUGINS_DIR = opj(SMASH_INSTALLATION_HOME, 'plugins')
THIS_DIR          = ops(__file__)[:-1]
SHELL_PATH        = os.environ['PATH'].split(':')

if HOME_BIN not in SHELL_PATH:
    raise SystemExit("""
Since smaSh is beta, scripts are currently installed to ~/bin directory, and I
notice that ~/bin is not in your $PATH.  Until system-wide installation is
implemented, can you add it there please?  Copy-pasta below might help you:

$ export PATH=$PATH:~/bin

""")

class install_data(_install_data):
    def copy_file(self, rel_src, dst_dir):
        """ """
        if not ope(rel_src):
            err = 'ERROR:\n\t{0} does not exist.\n\ncheck that your working directory is {1}'
            err = err.format(rel_src, THIS_DIR)
            raise SystemExit(err)
        else:
            link = 'sym' if 'develop' in sys.argv else None
            src_fname = ops(rel_src)[-1]
            dst_file = opj(dst_dir, src_fname)
            if ope(dst_file) or opil(dst_file):
                os.remove(dst_file)
            result = copy_file(os.path.abspath(rel_src), dst_dir, link=link, verbose=1)
            return result

class install(_install):
    def run(self):
        return self.run_command('install_data')

class develop(install_data):
    def run(self):
        self.run_command('install_data')

def _from(*args):
    """ NB: flat and not a recursive dir-walker """
    return [ opj(*(args + tuple([ ops(x)[-1] ]))) \
             for x in glob(opj(*(args + tuple(['*.py'])))) ]
PLUGINS = _from('src','plugins')
#[ opj('src','plugins', ops(x)[-1]) for x in glob(opj('src','plugins','*.py')) ]
LIB = _from('src','smash')
#[ opj('src','smash', ops(x)[-1]) for x in glob(opj('src','smash','*.py')) ]
CONFIG = ['smash.rc', 'src/plugins.json']
SCRIPTS = [ opj('scripts', 'smash'),
            opj('scripts', 'current_git_branch'),] + \
          [ opj('scripts', ops(x)[-1]) for x in glob(opj('scripts', '*')) ]

setup(
    name     = 'smash',
    cmdclass = dict(install      = install,
                    install_data = install_data,
                    develop      = develop,),
    data_files = [ ( SMASH_PLUGINS_DIR,       PLUGINS ),
                   ( HOME_BIN,                SCRIPTS ),
                   ( SMASH_INSTALLATION_HOME, CONFIG ),
                   ( SMASH_LIB_DST_DIR,        LIB ),]
    )
