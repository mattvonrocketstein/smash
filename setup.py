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
import os
import sys
import glob
from os.path import expanduser
from optparse import OptionParser

ope = os.path.exists
opj = os.path.join
opd = os.path.dirname
ops = os.path.split

HOME_BIN = expanduser('~/bin')
HOME_IPY = os.path.expanduser('~/.ipython')

SMASH_INSTALLATION_HOME = opj(HOME_IPY, 'smash')
SMASH_LIB_DST_DIR = opj(SMASH_INSTALLATION_HOME, 'smash')
SMASH_PLUGINS_DIR = opj(SMASH_INSTALLATION_HOME, 'plugins')

def niy(*args, **kargs):
    raise Exception, 'not implemented yet'

def doit(src, dest, effector=os.symlink):
    """ self.install() would be similar, without symlinks """
    try:
        if ope(dest): os.remove(dest)
        effector(src, dest)
    except OSError:
        print '-'*80
        print 'ERROR: dont you have permissions or something?\n  src="{0}"\n  dest="{1}"'.format(src,dest)
        print '-'*80
        raise

    else:
        print '{0} ---> {1}'.format(src, dest)

def only_py_files(dir, rel=False):
    result = glob.glob(opj(dir, '*.py'))
    if rel: result = [ ops(fname)[-1] for fname in result]
    return result

def msg_and_banner(msg):
    print '\n', msg, '\n', '='*len(msg)

class Setup:

    # only 'develop' is finished.
    install = build = niy

    @property
    def this_dir(self):
        return opd(os.path.abspath(__file__))

    @property
    def src_files_dir(self):
        return opj(self.this_dir, 'src')

    def dot_ipython_slash_smash(self, f):
        return opj(SMASH_INSTALLATION_HOME, ops(f)[1])


    def dot_ipython_slash_smash_plugins(self, f):
        return opj(SMASH_PLUGINS_DIR, ops(f)[1])

    def sanity(self):
        """ thinking of typing 'mkdir'? do it here. """
        if not ope(HOME_IPY):
            err = ('\nyou do not have a ~/.ipython directory.  whats up with that?'
                   ' (also, smash needs ipython==0.10)')
            raise SystemExit(err)

        dir2role = {
            SMASH_INSTALLATION_HOME:'creating smash installation directory',
            SMASH_PLUGINS_DIR:'creating plugins directory for smash installation',
            SMASH_LIB_DST_DIR:'creating smash lib dir for smash installation',}

        for d in dir2role:
            if not ope(d):
                print dir2role[d], d

    def develop(self):
        """ """
        def check_stale_files():
            """ find/remove files that are in ~/.ipython/smash
                but not in <InstallRoot>/src/
            """
            two_dirs = [ set(only_py_files(d, rel=True)) \
                         for d in [SMASH_INSTALLATION_HOME, self.src_files_dir] ]
            new, original = two_dirs
            diff = new - original
            if diff:
                msg_and_banner('detected stale files')
                for fname in diff:
                    print '{0} is in {1} but not {2}'.format(fname, SMASH_INSTALLATION_HOME, self.src_files_dir)
                    os.remove(opj(SMASH_INSTALLATION_HOME, fname))

        def install_plugins():
            msg_and_banner('installing symlinks for support libraries')
            files = only_py_files(opj(self.src_files_dir, 'plugins'))
            for src in files:
                dest = self.dot_ipython_slash_smash_plugins(src)
                doit(src, dest)

        def install_smash_lib():
            msg_and_banner('installing smash library')
            smash_lib_src_dir = opj(self.src_files_dir, 'smash')
            for fname in only_py_files(smash_lib_src_dir):
                dest = opj(SMASH_LIB_DST_DIR, ops(fname)[1])
                doit(fname, dest)

        def install_rc_file():
            msg_and_banner('installing symlinks for rc and conf files')
            dest = self.dot_ipython_slash_smash('smash.rc')
            smash_rc = opj(self.this_dir, 'smash.rc')
            src  = opj(self.this_dir, smash_rc)
            doit(src, dest)
            plugins_json = opj(self.src_files_dir, 'plugins.json')
            doit(plugins_json, self.dot_ipython_slash_smash(plugins_json))

        def install_scripts():
            SHELL_PATH = os.environ['PATH'].split(':')
            if HOME_BIN in SHELL_PATH: rdest = HOME_BIN
            # FIXME: this maybe should be a fatal error or have a backup policy...
            else: rdest = SMASH_INSTALLATION_HOME
            msg_and_banner('installing links for smash executable and other scripts ({0})'.format(rdest))
            for fname in os.listdir(opj(self.this_dir, 'scripts')):
                src = opj(self.this_dir, 'scripts', fname)
                dest = opj(rdest, fname)
                doit(src, dest)
            if rdest!=HOME_BIN:
                warning=('WARNING: not found ~/bin... will install to {0}'
                         ' (copy it out of there yourself if you want to)')
                print warning.format(rdest)

        self.sanity()
        install_smash_lib()
        install_plugins()
        install_rc_file()
        install_scripts()
        check_stale_files()


setup = Setup()

if __name__=='__main__':
    parser = OptionParser()
    opts, args  = parser.parse_args(sys.argv)
    args        = args[1:]
    if not args: raise SystemExit('pass args')
    instruction = args[0]
    if instruction not in 'build install develop'.split():
        raise SystemExit('Use one of these arguments: build, install develop"')
    else:
        instruction = getattr(setup, instruction)
        instruction()
