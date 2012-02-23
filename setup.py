""" setup.py for smash: the smart shell
"""
import os
import sys
from optparse import OptionParser



class ops:

    def compute_dest(self, f):
        return os.path.join(self.ipy_dir, os.path.split(f)[1])

    def build(self):
        pass

    def install(self):
        pass

    @property
    def this_dir(self):
        return os.path.dirname(os.path.abspath(__file__))
    def compute_src(self,f):
        return os.path.join(self.this_dir,'src',f)
    @property
    def filez(self):
        items = [ self.compute_src(x) for x in \
                  os.listdir(os.path.join(self.this_dir, 'src')) ]
        return items

    @property
    def ipy_dir(self):
        return os.path.expanduser('~/.ipython')

    def sanity(self):
        if not os.path.exists(self.ipy_dir):
            err = 'you do not have a ~/.ipython directory.  whats up with that?'
            raise SystemExit(err)

    def develop(self):
        self.sanity()
        print 'symlinking'
        msh_file = os.path.join(os.path.dirname(__file__), 'msh.rc')

        for src in self.filez:
            dest = self.compute_dest(src)
            os.remove(dest)
            #print src, dest
            os.symlink(src, dest)
            print '   ', src, '--->', dest

        dest = self.compute_dest('msh.rc')
        os.remove(dest)
        src = os.path.join(os.path.abspath(os.path.dirname(__file__)), msh_file)
        print '   ', src, '--->', dest
        os.symlink(src, dest)

ops = ops()

if __name__=='__main__':
    parser = OptionParser()
    opts, args  = parser.parse_args(sys.argv)
    args        = args[1:]
    if not args: raise SystemExit('pass args')
    instruction = args[0]
    if instruction not in 'build install develop'.split():
        raise SystemExit('Use one of these arguments: build, install develop"')
    instruction = getattr(ops,instruction)
    instruction()
    #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    #develop()
