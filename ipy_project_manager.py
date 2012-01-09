""" ipy_project_manager

    support for virtual-env management and other goodies
"""
import os
import sys

get_path = lambda: os.environ['PATH']
to_vbin = lambda venv: os.path.join(venv, 'bin')

class Project(object):
    """ class for holding Project abstractions.
        in the simplest case, beginning work on
        on a project just means changing directories.

        TODO: should really rename to 'projectman' or something
    """
    dir = None

    def __init__(self,name):
        self.name = name

    @classmethod
    def bind(kls, name, dir):
        """ named alias for changing directory to "dir". """
        @property
        def tmp(self):
            __IPYTHON__.ipmagic('cd '+dir)
            p = Project(name)
            p.dir = dir
            return p
        setattr(kls, name, tmp)

    @classmethod
    def bind_all(kls, dir):
        """ """
        print 'project-manager: binding', dir
        for name in os.listdir(dir):
            kls.bind(name,os.path.join(dir,name))

    def __repr__(self):
        return 'project: ' + self.name

    @classmethod
    def deactivate(self):
        path = get_path('PATH')
        path = path.split(':')
        venv = os.environ['VIRTUAL_ENV']
        assert os.path.exists(venv),'wont deactivate a relocated venv'
        vbin = to_vbin(venv)
        if vbin in path:
            print 'venv-manager: removing old venv bin', vbin
            path.remove(vbin)
            os.environ['PATH'] = ':'.join(path)
        print 'venv-manager: cleaning sys.path'
        nn=[]
        for entry in sys.path:
            if entry and not entry.startswith(venv):
                nn.append(entry)
        sys.path=nn

    @classmethod
    def activate(self,obj):
        self.deactivate()
        if isinstance(obj, str):
            if is_venv(obj):
                vbin = to_vbin(obj)
                path = get_path().split(':')
                os.environ['PATH']= ':'.join([vbin] + path)
                print 'venv-manager: adding %s to PATH and rehashing aliases' % vbin
                __IPYTHON__.ipmagic('rehash')
                sandbox = dict(__file__ = os.path.join(vbin,'activate_this.py'))
                execfile(os.path.join(vbin,'activate_this.py'),sandbox)
                print sandbox.keys()
            else:
                raise Exception,'directory is not a venv'

        else:
            assert isinstance(obj, Project), str(type(obj))
            return self.activate(obj.dir)


def is_venv(dir):
    y = 'lib bin include'.split()
    x = os.listdir(dir)
    if all([y1 in x for y1 in y]):
        return True
