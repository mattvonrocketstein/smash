""" setup.py for smash:the smart shell

    At the moment this setup is very hackish and nonstandard.

    A container virtualenvironment at ~/.smash is forced, and
    system-level installation is not possible.

"""
import os, sys
import fnmatch
from glob import glob
from os.path import expanduser
from collections import defaultdict
from distutils.core import setup
from distutils.file_util import copy_file
from distutils.command.install import install as _install
from distutils.command.install_data import install_data as _install_data

## begin aliases
################################################################################
ope  = os.path.exists
opj  = os.path.join
opd  = os.path.dirname
opil = os.path.islink
ops  = os.path.split

## begin constants
################################################################################
HOME_BIN    = expanduser('~/bin')
HOME_IPY    = os.path.expanduser('~/.smash')
VENV_PIP    = opj(HOME_IPY, 'bin', 'pip')
VENV_PY    = opj(HOME_IPY, 'bin', 'python')
THESE_DIR_COMPONENTS    = ops(__file__)[:-1]
SHELL_PATH  = os.environ['PATH'].split(':')
SMASH_BIN_DIR = opj(HOME_IPY, 'bin')
SMASH_ACTUAL_SHELL = opj(os.path.sep.join(THESE_DIR_COMPONENTS),'scripts','smash_actual_shell')
SMASH_INSTALLATION_HOME = HOME_IPY
SMASH_LIB_DST_DIR = opj(SMASH_INSTALLATION_HOME, 'smashlib')
SMASH_PLUGINS_DIR = opj(SMASH_INSTALLATION_HOME, 'plugins')
SMASH_CONFIG_DIR  = opj(SMASH_INSTALLATION_HOME, 'etc')

## begin classes
################################################################################
class install_data(_install_data):
    def copy_file(self, rel_src, dst_dir):
        """ TODO: DOX """
        if not ope(rel_src):
            err = 'ERROR:\n\t{0} does not exist.\n\ncheck that your working directory is {1}'
            err = err.format(rel_src, THESE_DIR_COMPONENTS)
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

## begin functions
################################################################################
def run_pip():
    """ """
    pip_cmd  = '{venv_pip} install -r {smash_reqs} --timeout=120'
    req_file = opj(*(THESE_DIR_COMPONENTS + ('requirements.txt',)))
    cmd = pip_cmd.format(venv_pip=VENV_PIP, smash_reqs=req_file)
    error = os.system(cmd)
    return error

def venv_gen_ipython():
    """ this if for creating the ipython directory, etc, just
        in the event case $USER has never tried it before at all.
    """
    if not ope(expanduser('~/.ipython')):
        cmd = ("import os; "
               " from IPython.genutils import get_ipython_dir;"
               " from IPython.iplib import user_setup;"
               " rc_suffix = '' if os.name == 'posix' else '.ini';"
               "user_setup(get_ipython_dir(), rc_suffix, mode='install', interactive=False)")
        t = '{python} -c "{cmd}"'.format(python=VENV_PY,cmd=cmd)
        return os.system(t)

def create_virtualenv(abspath):
    print "Creating virtual-environment: {0}".format(abspath)
    #cmd = 'virtualenv --no-site-packages {0}'
    cmd = 'virtualenv {0}'
    cmd = cmd.format(abspath)
    return os.system(cmd)

def _from(*args, **kargs):
    """ generates lists of files in the style that setup() expects.
        only python files!  no emacs tmp files or vcs junk allowed.

        NB: expects flatness in python packages (not a recursive dir-walker)
    """
    suffix = kargs.pop('suffix', '*.py')
    return [ opj(*(args + tuple([ ops(x)[-1] ]))) \
             for x in glob(opj(*(args + tuple([suffix])))) ]

def _from2(*args, **kargs):
    """ generates lists of files in the style that setup() expects.
        only python files!  no emacs tmp files or vcs junk allowed.

        this version IS a recursive walker.
        TODO: deprecate _from() to just use this
    """
    matches = defaultdict(lambda:[])
    suffix = kargs.pop('suffix', '*.py')
    for root, dirnames, filenames in os.walk(opj(*args)):
        for filename in fnmatch.filter(filenames, suffix):
            matches[root[root.find('smashlib'):]].append(os.path.join(root, filename))
    return matches

## entry point
################################################################################
if HOME_BIN not in SHELL_PATH:
    raise SystemExit("""
Since SmaSh is beta, scripts are currently installed to ~/bin directory, and I
notice that ~/bin is not in your $PATH.  Until system-wide installation is
implemented, can you add it there please?\n\nThe copy-pasta below might help you:

    $ mkdir ~/bin; export PATH=$PATH:~/bin

You may also want to change $PATH in your .bashrc or whatever, please consult
your shell's documentation.
""")

has_virtualenv = not os.system('which virtualenv > /dev/null 2>&1')
if not has_virtualenv:
    raise SystemExit(("No virtualenv found.\n"
                      "Do something like this to install it:\n"
                      "  for debian/ubuntu: "
                      "\"apt-get install python-virtualenv\""))

if not ope(HOME_IPY):
    print HOME_IPY, 'doesnt exist'
    error = create_virtualenv(HOME_IPY)
    if error: raise SystemExit('Error creating virtual-environment for shell')
    print 'Finished creating virtual-environment.\n'
pip_error = run_pip()
if pip_error:
    raise SystemExit('Failed to install requirements into virtual-environment')
else: print 'Finished installing requirements.\n'
initialize_ipy_error = venv_gen_ipython()
if initialize_ipy_error:
    raise SystemExit('Failed to init ipython using virtual-environment')
else:
    print 'Finished initializing ~/.ipython.\n'

LIB      = _from2('lib','smashlib')
PLUGINS  = _from('lib','plugins')
CONFIG   = [ opj('config', 'smash.rc'),
             opj('config', 'plugins.json'),
             opj('config', 'projects.json'),
             opj('config', 'editor.json'),
             opj('config', 'hosts.json'),
             opj('config', 'bookmarks.json'),
        ]
SCRIPTS = [ opj('scripts', 'smash'),
            opj('scripts', 'current_git_branch'),
            ] + \
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
        ( SMASH_BIN_DIR,        [SMASH_ACTUAL_SHELL] ),
        ])

for smashlib_sub_pkg_dir in LIB:
    kargs['data_files'].append(
          ( opj(SMASH_INSTALLATION_HOME,
                smashlib_sub_pkg_dir),
            LIB[smashlib_sub_pkg_dir]))

IPY_BASE = []
for x in _from('ipython_base', suffix='*'):
    rel = os.path.split(x)[-1]
    if not ope(opj(expanduser('~/.ipython'), rel)):
        IPY_BASE.append(x)
kargs['data_files'] += [ ( HOME_IPY, IPY_BASE), ]

kargs.update(long_description=kargs['description']+'. Read more: '+kargs['url'])
setup(**kargs)
