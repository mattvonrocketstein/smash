""" ipy_project_manager

    support for virtual-env management and other goodies
 """
import os
import sys
from collections import defaultdict
get_path = lambda: os.environ['PATH']
to_vbin = lambda venv: os.path.join(venv, 'bin')

class Project(object):
    """ class for holding Project abstractions.
        in the simplest case, beginning work on
        on a project just means changing directories.

        TODO: should really rename to 'projectman' or something
    """
    dir = None

    def ipy_install(self,name='proj'):
        """ binds self into interactive shell namespace """
        __IPYTHON__.shell.user_ns[name] = self

    def pre_activate(self, name, f):
        self._pre_invokage[name] += [f]

    def __init__(self,name):
        self.name = name
        self._pre_invokage  = defaultdict(lambda: [])
        self._post_invokage = defaultdict(lambda: [])

    @classmethod
    def bind(kls, name, dir):
        """ named alias for changing directory to "dir". """
        p = Project(name)
        p.dir = dir
        @property
        def tmp(self):
            [ f() for f in self._pre_invokage[name] ]
            __IPYTHON__.ipmagic('cd ' + p.dir)
            [ f() for f in self._post_invokage[name] ]
            return p
        setattr(kls, name, tmp)

    @classmethod
    def bind_all(kls, dir):
        """ """
        print 'project-manager: binding', dir
        for name in os.listdir(dir):
            kls.bind(name, os.path.join(dir,name))

    def __repr__(self):
        return 'project: ' + self.name

    @classmethod
    def deactivate(self):
        """ TODO: move this to ipy_venv_support """
        try:
            venv = os.environ['VIRTUAL_ENV']
        except KeyError:
            return
        else:
            assert os.path.exists(venv), 'wont deactivate a relocated venv'
            path = get_path()
            path = path.split(':')

            # clean $PATH according to bash..
            # TODO: also rehash
            vbin = to_vbin(venv)
            if vbin in path:
                print 'venv-manager: removing old venv bin from PATH', vbin
                path.remove(vbin)
                os.environ['PATH'] = ':'.join(path)

            # clean sys.path according to python..
            # stupid, but this seems to work
            print 'venv-manager: cleaning sys.path'
            nn = []
            for entry in sys.path:
                if entry and not entry.startswith(venv):
                    nn.append(entry)
            sys.path = nn

    @classmethod
    def activate(self, obj):
        """ TODO: move/combine this to ipy_venv_support

            activating a project is different than activating
            a venv (but it might include activating a venv)
        """
        self.deactivate()
        if isinstance(obj, str):
            if is_venv(obj):
                vbin = to_vbin(obj)
                path = get_path().split(':')
                os.environ['PATH'] = ':'.join([vbin] + path)
                print 'venv-manager: adding %s to PATH and rehashing aliases' % vbin
                __IPYTHON__.ipmagic('rehash')
                sandbox = dict(__file__ = os.path.join(vbin, 'activate_this.py'))
                execfile(os.path.join(vbin,'activate_this.py'),sandbox)
            else:
                print 'venv-manager: not a venv..', obj
                searchsub = 'venv node'.split()
                for name in searchsub:
                    try:
                        tmp = self.activate(os.path.join(obj, name))
                        if tmp:
                            return tmp
                    except OSError:
                        pass


        else:
            assert isinstance(obj, Project), str(type(obj))
            return self.activate(obj.dir)


def is_venv(dir):
    """ naive.. seems to work """
    y = 'lib bin include'.split()
    x = os.listdir(dir)
    if all([y1 in x for y1 in y]):
        return True
