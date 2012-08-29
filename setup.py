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

def niy(*args, **kargs):
    raise Exception, 'not implemented yet'

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
        return opj(self.ipy_dir, 'smash', ops(f)[1])

    @property
    def files(self):
        items = [ opj(self.src_files_dir, x)
                  for x in only_py_files(self.src_files_dir) ]
        return items

    @property
    def ipy_dir(self):
        return os.path.expanduser('~/.ipython')

    @property
    def smash_dir(self):
        return opj(self.ipy_dir, 'smash')

    def sanity(self):
        """ """
        if not ope(self.ipy_dir):
            err = ('\nyou do not have a ~/.ipython directory.  whats up with that?'
                   ' (also, smash needs ipython==0.10)')
            raise SystemExit(err)

        if not ope(self.smash_dir):
            print 'creating ', self.smash_dir
            os.mkdir(self.smash_dir)

    def develop(self):
        """ """

        def check_stale_files():
            """ find/remove files that are in ~/.ipython/smash
                but not in <InstallRoot>/src/
            """
            two_dirs = [ set(only_py_files(d, rel=True)) \
                         for d in [self.smash_dir, self.src_files_dir] ]
            new, original = two_dirs
            diff = new - original
            if diff:
                msg_and_banner('detected stale files')
                for fname in diff:
                    print '{0} is in {1} but not {2}'.format(fname, self.smash_dir, self.src_files_dir)
                    os.remove(opj(self.smash_dir, fname))

        def install_plugins():
            msg_and_banner('installing symlinks for support libraries')
            for src in self.files:
                dest = self.dot_ipython_slash_smash(src)
                doit(src, dest)

        def install_smash_lib():
            msg_and_banner('installing smash library')
            smash_lib_src_dir = opj(self.src_files_dir, 'smash')
            smash_lib_dst_dir = opj(self.ipy_dir, 'smash', 'smash')
            if not ope(smash_lib_dst_dir):
                print 'creating ', smash_lib_dst_dir
                os.mkdir(smash_lib_dst_dir)

            for fname in only_py_files(smash_lib_src_dir):
                dest = opj(smash_lib_dst_dir, ops(fname)[1])
                doit(fname, dest)

        def install_rc_file():
            msg_and_banner('installing symlinks for rc and conf files')
            dest = self.dot_ipython_slash_smash('smash.rc')
            smash_rc = opj(self.this_dir, 'smash.rc')
            src  = opj(self.this_dir, smash_rc)
            doit(src, dest)
            plugins_json = opj(self.this_dir, 'src', 'plugins.json')
            doit(plugins_json, self.dot_ipython_slash_smash(plugins_json))

        def install_scripts():
            msg_and_banner('installing links for smash executable and other scripts')
            dot_ipy_smash_dir = opj(self.ipy_dir, 'smash')
            home_bin          = expanduser('~/bin')
            if home_bin in os.environ['PATH'].split(':'):
                print '  found ~/bin... will install there'
                rdest = home_bin
            else:
                print ('not found ~/bin... will install to {0}'
                       ' (copy it out of there yourself if you want to)').format(dot_ipy_smash_dir)
                dest = dot_ipy_smash_dir

            for rsrc in os.listdir(opj(self.this_dir, 'scripts')):
                src = opj(self.this_dir, 'scripts', rsrc)
                dest = opj(rdest, rsrc)
                doit(src, dest)

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
