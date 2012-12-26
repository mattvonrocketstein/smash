""" smashlib.venv
"""

import types
import os, sys, glob

from smashlib.util import opj, bus, report,truncate_fpath

get_path   = lambda: os.environ['PATH']
get_venv   = lambda: os.environ['VIRTUAL_ENV']
to_vbin    = lambda venv: opj(venv, 'bin')
to_vlib    = lambda venv: opj(venv, 'lib')

def is_venv(dir):
    """ naive.. seems to work
        TODO: find a canonical version of this function or refine it
    """
    dir_names = 'lib bin include'.split()
    try:
        x = os.listdir(dir)
    except OSError:
        # permission denied or something?
        return False
    else:
        if all([y1 in x for y1 in dir_names]):
            return True
    return False

def _contains_venv(_dir):
    """ ascertain whether _dir is, or if it contains, a venv.

        returns the first matching path according to the heuritic
    """
    if is_venv(_dir):
        return _dir
    searchsub = 'venv node'.split() # FIXME: abstract
    searchsub = [ opj(_dir, name) for name in searchsub ]
    searchsub = [ name for name in searchsub if os.path.exists(name) ]
    for name in searchsub:
        if is_venv(name):
            return name

class VenvMixin(object):

    @classmethod
    def deactivate(self):
        """ TODO: move this to ipy_venv_support """
        from smashlib.projects import Project
        bus().publish('pre_deactivate',name=Project('__smash__').CURRENT_PROJECT)
        try:
            venv = get_venv()
        except KeyError:
            return False
        else:
            if not os.path.exists(venv):
                raise RuntimeError,'refusing to deactivate (relocated?) venv'
            del os.environ['VIRTUAL_ENV']
            path = get_path()
            path = path.split(':')

            # clean $PATH according to bash..
            # TODO: also rehash?
            vbin = to_vbin(venv)
            if vbin in path:
                report.venv_mixin('removing old venv bin from PATH: ' + truncate_fpath(str(vbin)))
                path.remove(vbin)
                os.environ['PATH'] = ':'.join(path)

            # clean sys.path according to python..
            # stupid, but this seems to work
            import smashlib
            report.venv_mixin('cleaning sys.path')
            new_path = []
            for entry in sys.path:
                if entry and not entry.startswith(venv):
                    new_path.append(entry)
                else:
                    if entry.startswith(smashlib._meta['SMASH_DIR']) and \
                       'IPython' in entry:
                        # careful, dont remove our bootstraps.
                        # specifically this will break --project=..
                        # invocation
                        new_path.append(entry)
                    else:
                        #print 'cleaning: ',entry
                        pass

            sys.path = new_path
            # TODO: clean sys.modules?
            bus().publish('post_deactivate',name=Project('__smash__').CURRENT_PROJECT)
            return True

    @classmethod
    def _activate_str(self, obj):
        if is_venv(obj):
            vbin = to_vbin(obj)
            vlib = to_vlib(obj)

            # compute e.g. <venv>/lib/python2.6.
            # we call bullshit if they have a more than one dir;
            # it might be a chroot but i dont think it's a venv
            python_dir = glob.glob(opj(vlib, 'python*/'))
            if not 0 < len(python_dir) < 2:
                err = 'Not sure how to handle this; zero or 1+ dirs matching "python*"'
                raise RuntimeError, err
            python_dir = python_dir[0]

            # this bit enables switching between two venv's
            # that might be "no-global-site" vs "use-global-site"
            site_file = opj(python_dir, 'site.py')
            assert os.path.exists(site_file)
            tmp = dict(__file__=site_file)
            execfile(site_file, tmp)
            tmp['main']()

            # some environment variable manipulation that would
            # normally be done by 'source bin/activate', but is
            # not handled by activate_this.py
            path = get_path().split(':')
            os.environ['PATH'] = ':'.join([vbin] + path)
            os.environ['VIRTUAL_ENV'] = obj
            report.venv_mixin('\tadding "%s" to PATH; rehashing aliases' % truncate_fpath(vbin))
            sandbox = dict(__file__ = opj(vbin, 'activate_this.py'))
            execfile(opj(vbin, 'activate_this.py'), sandbox)

            # libraries like 'datetime' can fail on import if this isnt done,
            # i'm not sure why activate_this.py doesnt accomplish it.
            dynload = opj(python_dir, 'lib-dynload')
            sys.path.append(dynload)

            # rehash aliases based on $PATH, then
            # reinstall anything else we killed in
            # the rehash
            __IPYTHON__.ipmagic('rehashx')

        else:
            report.venv_mixin('\ttoplevel@"{0}" is not a venv, looking elsewhere'.format(truncate_fpath(obj)))
            path = _contains_venv(obj)
            if path:
                return self._activate_str(path)

    @classmethod
    def _activate_project(self, obj):
        """ #FIXME: this is in the wrong file.. """
        result = self._activate_str(obj.dir)
        bus().publish('post_activate.' + obj.name)
        return result

    @property
    def activate(self):
        return self._activate(self)

    @classmethod
    def _activate(self, obj):
        """
            activating a project (referred to instead as "invoking" is
            different than activating a venv (but it might include
            activating a venv)
        """
        # TODO: move/combine this to ipy_venv_support ?
        # FIXME: get rid of Project-dep ?
        from smashlib.projects import Project as ProjectClass

        self.deactivate()
        if isinstance(obj, types.StringTypes):
            result = self._activate_str(obj)
        #elif type(obj).__name__ == ProjectClass.__name__:
        elif isinstance(obj, ProjectClass):
            bus().publish('pre_activate', name=obj.name, )
            result = self._activate_project(obj)
            bus().publish('post_activate', name=obj.name, )
        else:
            err = "Don't know how to activate an object like '" + \
                  str(type(obj)) + '"'
            raise RuntimeError, err
        return result
