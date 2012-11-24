""" setup.py for smash:the smart shell

    At the moment this setup is very hackish and nonstandard.  The main reason
    for that is because to use smash you should NOT have to perform either of
    the following:

        1) system-wide installation
        2) installation into some one-off virtual-environment

    System wide installation is not elegant for obvious reasons, but avoiding
    even a virtual-environment goes against a lot of python developers
    instincts.

    However, the reason for avoiding a virtual-environment is simple: one of
    the things that smash is designed around is easily managing virtual
    environments!  So you can imagine that having activated nested virtual
    environments can lead to surprising consequences.. it's best to avoid it
    altogether.  See the `README.rst` for a high-level description of what
    this setup actually does.

"""
import os, sys
from glob import glob
from os.path import expanduser
from distutils.core import setup
from distutils.file_util import copy_file
from distutils.command.install import install as _install
from distutils.command.install_data import install_data as _install_data

ope  = os.path.exists
opj  = os.path.join
opd  = os.path.dirname
opil = os.path.islink
ops  = os.path.split

HOME_BIN    = expanduser('~/bin')
HOME_IPY    = os.path.expanduser('~/.ipython')
THIS_DIR    = ops(__file__)[:-1]
SHELL_PATH  = os.environ['PATH'].split(':')

SMASH_INSTALLATION_HOME = opj(HOME_IPY, 'smash')
SMASH_LIB_DST_DIR = opj(SMASH_INSTALLATION_HOME, 'smash')
SMASH_PLUGINS_DIR = opj(SMASH_INSTALLATION_HOME, 'plugins')
SMASH_CONFIG_DIR  = opj(SMASH_INSTALLATION_HOME, 'config')

if HOME_BIN not in SHELL_PATH:
    raise SystemExit("""
Since SmaSh is beta, scripts are currently installed to ~/bin directory, and I
notice that ~/bin is not in your $PATH.  Until system-wide installation is
implemented, can you add it there please?  Copy-pasta below might help you:

$ export PATH=$PATH:~/bin

""")

if not ope(expanduser('~/.ipython')):
    raise SystemExit("No .ipython folder in your home directory?")

class install_data(_install_data):
    def copy_file(self, rel_src, dst_dir):
        """ TODO: DOX """
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
            result = copy_file(os.path.abspath(rel_src),
                               dst_dir, link=link, verbose=1)
            return result

class install(_install):
    def run(self):
        return self.run_command('install_data')

class develop(install_data):
    def run(self):
        self.run_command('install_data')

def _from(*args, **kargs):
    """ generates lists of files in the style that setup() expects.
        only python files!  no emacs tmp files or vcs junk allowed.

        NB: expects flatness in python packages (not a recursive dir-walker)
    """
    suffix = kargs.pop('suffix', '*.py')
    return [ opj(*(args + tuple([ ops(x)[-1] ]))) \
             for x in glob(opj(*(args + tuple([suffix])))) ]

LIB      = _from('src','smash')
IPY_BASE = _from('ipython_base')
PLUGINS  = _from('src','plugins')
CONFIG   = [ opj('config', 'smash.rc'),
             opj('config', 'plugins.json')
        ]
SCRIPTS = [ opj('scripts', 'smash'),
            opj('scripts', 'current_git_branch'),] + \
          _from('scripts')

kargs = dict(
    name         = 'smash',
    author       = 'mattvonrocketstein, in the gmails',
    version      = '0.1',
    description  = 'smaSh: a smarter shell',
    url          = 'http://github.com/mattvonrocketstein/smash',
    license      = 'MIT',
    keywords     = 'system shell',
    platforms    = 'any',
    zip_safe     = False,
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 000 - Experimental',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent', ],
    cmdclass = dict(install      = install,
                    install_data = install_data,
                    develop      = develop,),
    data_files = [
        ( SMASH_PLUGINS_DIR,       PLUGINS ),
        ( HOME_BIN,                SCRIPTS ),
        ( SMASH_CONFIG_DIR,        CONFIG ),
        ( SMASH_LIB_DST_DIR,       LIB ),])

# FIXME: this might overwrite existing ipython configuration,
# but if nothing is there then smash will not be able to load
kargs['data_files']+= [ ( SMASH_INSTALLATION_HOME, IPY_BASE), ]

kargs.update(long_description=kargs['description']+'. Read more: '+kargs['url'])
setup(**kargs)
