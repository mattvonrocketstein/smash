""" smash.venv
"""
import os
import sys

get_path   = lambda: os.environ['PATH']
get_venv   = lambda: os.environ['VIRTUAL_ENV']
to_vbin    = lambda venv: os.path.join(venv, 'bin')
os.path.expanduser = os.path.os.path.expanduser

def is_venv(dir):
    """ naive.. seems to work

        TODO: find a canonical version of this function or refine it
    """
    y = 'lib bin include'.split()
    x = os.listdir(dir)
    if all([y1 in x for y1 in y]):
        return True

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
            os.environ['VIRTUAL_ENV'] = obj
            self.report('      adding "%s" to PATH; rehashing aliases' % vbin)
            sandbox = dict(__file__ = os.path.join(vbin, 'activate_this.py'))
            execfile(os.path.join(vbin,'activate_this.py'),sandbox)
            __IPYTHON__.ipmagic('rehashx')
            from ipy_smash_aliases import install_aliases
            install_aliases()

        else:
            self.report('  not a venv.. ' + obj)
            path = self._contains_venv(obj)
            if path:
                return self._activate(path)

    @classmethod
    def _activate_project(self,obj):
        """ """
        result = self._activate_str(obj.dir)
        [ f() for f in self._post_activate[obj.name] ]

    @property
    def activate(self):
        return self._activate(self)

    @property
    def aliases(self):
        return self.config['aliases']


    @classmethod
    def _activate(self, obj):
        """ TODO: move/combine this to ipy_venv_support

            activating a project (referred to instead as "invoking" is
            different than activating a venv (but it might include
            activating a venv)

             FIXME: get rid of Project-dep
        """
        from ipy_project_manager import Project
        self.deactivate()
        if isinstance(obj, str):
            return self._activate_str(obj)
        elif isinstance(obj, Project):
            return self._activate_project(obj)
        else:
            err = "Don't know how to activate an object like '" + str(type(obj)) + '"'
            raise Exception, err
