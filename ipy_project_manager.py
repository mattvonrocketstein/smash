""" ipy_project_manager

    support for virtual-env management and other goodies
 """
import os
import sys
from collections import defaultdict

from ipy_profile_msh import colorize
from ipy_bonus_yeti import post_hook_for_magic

get_path = lambda: os.environ['PATH']
get_venv = lambda: os.environ['VIRTUAL_ENV']
to_vbin = lambda venv: os.path.join(venv, 'bin')

class VenvMixin(object):
    @classmethod
    def deactivate(self):
        """ TODO: move this to ipy_venv_support """
        try:
            venv = get_venv()
        except KeyError:
            return False
        else:
            assert os.path.exists(venv), 'wont deactivate a relocated venv'
            path = get_path()
            path = path.split(':')

            # clean $PATH according to bash..
            # TODO: also rehash?
            vbin = to_vbin(venv)
            if vbin in path:
                self.report('removing old venv bin from PATH', vbin)
                path.remove(vbin)
                os.environ['PATH'] = ':'.join(path)

            # clean sys.path according to python..
            # stupid, but this seems to work
            self.report('cleaning sys.path')
            nn = []
            for entry in sys.path:
                if entry and not entry.startswith(venv):
                    nn.append(entry)
            sys.path = nn
            return True

    @classmethod
    def _contains_venv(self, _dir):
        """ ascertain whether _dir is, or if it contains, a venv.

            returns the first matching path according to the heuritic
        """
        if is_venv(_dir):
            return _dir
        searchsub = 'venv node'.split()
        searchsub = [ os.path.join(_dir, name) for name in searchsub ]
        searchsub = [ name for name in searchsub if os.path.exists(name) ]
        for name in searchsub:
            self.report('    trying "'+name+'"')
            if is_venv(name):
                return name

    @classmethod
    def _activate_str(self, obj):
        if is_venv(obj):
            vbin = to_vbin(obj)
            path = get_path().split(':')
            os.environ['PATH'] = ':'.join([vbin] + path)
            self.report('      adding "%s" to PATH; rehashing aliases' % vbin)
            sandbox = dict(__file__ = os.path.join(vbin, 'activate_this.py'))
            execfile(os.path.join(vbin,'activate_this.py'),sandbox)
            __IPYTHON__.ipmagic('rehashx')
        else:
            self.report('  not a venv.. ' + obj)
            path = self._contains_venv(obj)
            if path:
                return self.activate(path)

    @classmethod
    def _activate_project(self,obj):
        """ placeholder for when projects support
            post-venv-activation hooks
        """
        return self._activate_str(obj.dir)

    @classmethod
    def activate(self, obj):
        """ TODO: move/combine this to ipy_venv_support

            activating a project (referred to instead as "invoking" is
            different than activating a venv (but it might include
            activating a venv)

        """
        self.deactivate()
        if isinstance(obj, str):
            return self._activate_str(obj)
        elif isinstance(obj, Project):
            return self._activate_project(obj)
        else:
            err = "Don't know how to activate an object like '" + str(type(obj)) + '"'
            raise Exception, err

class Project(VenvMixin):
    """ class for holding Project abstractions. in the simplest case,
        beginning work on on a project just means changing directories.
        you can also work with python virtual environments like this:

        >>> proj.activate(proj.project_name)

        TODO: document difference between project "invokage" vs "activation"
        TODO: should really rename to 'projectman' or something
    """

    dir = None
    _paths = []

    def _announce_if_project(self):
        """ post-hook for ipython's magic "cd"

            this function will notice when you change directories
            into a place that is registered as a project.
        """
        _dir = os.getcwd()
        if _dir in self._paths:
            m1 = 'This directory is also a registered project.'
            m2 = '  You can activate it with "proj.activate(proj.{name})"'
            m2 = m2.format(name=os.path.split(_dir)[1])
            self.report(m1); self.report(m2)


    def _ipy_install(self,name='proj'):
        """ binds self into interactive shell namespace """
        __IPYTHON__.shell.user_ns[name] = self
        post_hook_for_magic('cd', self._announce_if_project)

    def pre_activate(self, name, f):
        """ """
        self._pre_invokage[name] += [f]

    def __init__(self, name):
        """ """
        self.name = name
        self._pre_invokage  = defaultdict(lambda: [])
        self._post_invokage = defaultdict(lambda: [])

    @classmethod
    def bind(kls, _dir, name=None):
        """ named alias for changing directory to "_dir". """
        if name is None:
            name=os.path.split(_dir)[1]
        p = Project(name)
        p.dir = _dir
        kls._paths += [_dir]
        @property
        def tmp(self):
            """ yeah this is a pretty awful hack..
                TODO: refactor it later
            """
            [ f() for f in self._pre_invokage[name] ]

            # grabs a magic "cd" function from ipython, but try to bypass
            # the now redundant _announce_if_project wrapper we installed
            # earlier
            cd_func = __IPYTHON__.magic_cd
            cd_func = getattr(cd_func, '_wrapped', cd_func)
            cd_func(p.dir)

            [ f() for f in self._post_invokage[name] ]
            return p

        setattr(kls, name, tmp)

    @classmethod
    def report(kls, *args):
        """ """
        if len(args)>1:
            print colorize('{red}project-manager:{normal}'),args
        else:
            print colorize('{red}project-manager:{normal} ') + args[0]

    @classmethod
    def bind_all(kls, _dir):
        """ binds every directory in _dir as a project """
        N=0
        for name in os.listdir(_dir):
            tmp = os.path.join(_dir,name)
            if os.path.isdir(tmp):
                N += 1
                kls.bind(tmp, name)
        kls.report('binding ' + _dir + ' (' + str(N) + ' projects found)')

    def __repr__(self):
        """ """
        return 'project: ' + self.name



def is_venv(dir):
    """ naive.. seems to work

        TODO: find a canonical version of this function or refine it
    """
    y = 'lib bin include'.split()
    x = os.listdir(dir)
    if all([y1 in x for y1 in y]):
        return True
