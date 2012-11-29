""" setup.py for smash:the smart shell

    At the moment this setup is very hackish and nonstandard.

    A container virtualenvironment at ~/.smash is forced, and
    system-level installation is not possible.

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
HOME_IPY    = os.path.expanduser('~/.smash')
THIS_DIR    = ops(__file__)[:-1]
SHELL_PATH  = os.environ['PATH'].split(':')
SMASH_BIN_DIR = opj(HOME_IPY, 'bin')
SMASH_ACTUAL_SHELL = opj(os.path.sep.join(THIS_DIR),'scripts','smash_actual_shell')
SMASH_INSTALLATION_HOME = HOME_IPY #opj(HOME_IPY, 'smash')
SMASH_LIB_DST_DIR = opj(SMASH_INSTALLATION_HOME, 'smash')
SMASH_PLUGINS_DIR = opj(SMASH_INSTALLATION_HOME, 'plugins')
SMASH_CONFIG_DIR  = opj(SMASH_INSTALLATION_HOME, 'etc')

def run_pip():
    cmd = '{venv_pip} install -r {smash_reqs}'.format(
        venv_pip=opj(HOME_IPY, 'bin', 'pip'),
        smash_reqs=opj(*(THIS_DIR + tuple(['requirements.txt']))))
    error = os.system(cmd)
    return error

    """
    execfile(athis)
    from pip.index import PackageFinder
    from pip.req import InstallRequirement, RequirementSet
    from pip.locations import build_prefix, src_prefix

    requirement_set = RequirementSet(
        build_dir=build_prefix,
        src_dir=src_prefix,
        download_dir=None)
    reqs = opj(*(THIS_DIR + tuple(['requirements.txt'])))
    reqs = open(reqs,'r')
    reqs = [x.strip() for x in reqs.readlines() if x.strip()]
    for req in reqs:
        requirement_set.add_requirement(
            InstallRequirement.from_line(req, None) )
    install_options = []
    global_options = []
    finder = PackageFinder(find_links=[],
                           index_urls=["http://pypi.python.org/simple/"])
    print "\nPreparing:{0}\n==================================".format(reqs)
    requirement_set.prepare_files(finder, force_root_egg_info=False, bundle=False)
    print "\nInstalling:{0}\n==================================".format(reqs)
    requirement_set.install(install_options, global_options)

    print "\nInstalled\n=================================="
    for package in requirement_set.successfully_installed: print package.name
    """
    # FIXME?: assumes no -e git+ssh bizness
    """
    unfound = []
    for req in reqs:
        try:
            __import__(req)
        except ImportError:
            unfound.append(req)
    import pip#raise Exception,unfound
    """

def create_virtualenv(abspath):
    print "Creating virtual-environment: {0}".format(abspath)
    return os.system('virtualenv --no-site-packages {0}'.format(abspath))

if HOME_BIN not in SHELL_PATH:
    raise SystemExit("""
Since SmaSh is beta, scripts are currently installed to ~/bin directory, and I
notice that ~/bin is not in your $PATH.  Until system-wide installation is
implemented, can you add it there please?  Copy-pasta below might help you:

$ export PATH=$PATH:~/bin

""")

if not ope(expanduser('~/.ipython')):
    raise SystemExit("No .ipython folder in your home directory?")

has_virtualenv = not os.system('which virtualenv > /dev/null 2>&1')
if not has_virtualenv:
    raise SystemExit(("No virtualenv found.\n"
                      "Do something like this to install it:\n"
                      "  for debian/ubuntu: "
                      "\"apt-get install python-virtualenv\""))

if not ope(HOME_IPY):
    error = create_virtualenv(HOME_IPY)
    if error: raise SystemExit('Error creating virtual-environment for shell')
    print 'Finished creating virtual-environment.\n'
    pip_error = run_pip()
else: pip_error = run_pip()
if pip_error:
    raise SystemExit('Failed to install requirements into virtual-environment')
else: print 'Finished installing requirements.\n'

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
PLUGINS  = _from('src','plugins')
CONFIG   = [ opj('config', 'smash.rc'),
             opj('config', 'plugins.json'),
             opj('config', 'projects.json')
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
        ( SMASH_BIN_DIR,        [SMASH_ACTUAL_SHELL] ),
        ( SMASH_LIB_DST_DIR,       LIB ),])

IPY_BASE = []
for x in _from('ipython_base', suffix='*'):
    rel = os.path.split(x)[-1]
    if not ope(opj(expanduser('~/.ipython'), rel)):
        IPY_BASE.append(x)
kargs['data_files'] += [ ( HOME_IPY, IPY_BASE), ]

kargs.update(long_description=kargs['description']+'. Read more: '+kargs['url'])
setup(**kargs)
