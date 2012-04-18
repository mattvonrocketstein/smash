""" setup.py for smash: the smart shell
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

class Setup:

    def build(self): pass
    def install(self): pass


    @property
    def this_dir(self):
        return opd(os.path.abspath(__file__))

    def compute_src(self,f): return opj(self.this_dir,'src',f)
    def compute_dest(self, f): return opj(self.ipy_dir, 'smash', ops(f)[1])



    @property
    def filez(self):
        items = [ self.compute_src(x) for x in \
                  glob.glob(opj(self.this_dir, 'src','*.py')) ]
        return items

    @property
    def ipy_dir(self):
        return os.path.expanduser('~/.ipython')

    @property
    def smash_dir(self):
        return opj(self.ipy_dir,'smash')

    def sanity(self):
        if not ope(self.ipy_dir):
            err = '\nyou do not have a ~/.ipython directory.'
            err+= 'whats up with that?  (i need ipython .10)'
            raise SystemExit(err)

        if not ope(self.smash_dir):
            print 'creating ',self.smash_dir
            os.mkdir(self.smash_dir)

    def develop(self):
        def doit(src, dest):
            try:
                if ope(dest): os.remove(dest)
                os.symlink(src, dest)
            except OSError:
                print '-'*80+'\ndont you have permissions or something?\n'+'-'*80
                raise
            else: print ' ', src, '--->', dest
        self.sanity()
        print 'installing symlinks for support libraries'
        msh_file = opj(opd(__file__), 'smash.rc')
        for src in self.filez:
            dest = self.compute_dest(src)
            doit(src, dest)
        dest = self.compute_dest('smash.rc')
        src = opj(self.this_dir, msh_file)
        doit(src, dest)

        print '\ninstalling smash executable and other scripts'
        default_bin = opj(self.ipy_dir, 'smash')
        home_bin = expanduser('~/bin')
        #src = opj(self.this_dir, 'scripts', 'smash')
        if home_bin in os.environ['PATH'].split(':'):
            print '  found ~/bin... will install there'
            rdest = home_bin
        else:
            print '  not found ~/bin... will install to', default_bin
            print '(copy it out of there yourself if you want to)'
            dest = default_bin
        for rsrc in os.listdir(opj(self.this_dir, 'scripts')):
            src = opj(self.this_dir, 'scripts', rsrc)
            dest = opj(rdest, rsrc)
            doit(src, dest)

setup = Setup()

if __name__=='__main__':
    parser = OptionParser()
    opts, args  = parser.parse_args(sys.argv)
    args        = args[1:]
    if not args: raise SystemExit('pass args')
    instruction = args[0]
    if instruction not in 'build install develop'.split():
        raise SystemExit('Use one of these arguments: build, install develop"')
    instruction = getattr(setup, instruction)
    instruction()
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    #develop()
