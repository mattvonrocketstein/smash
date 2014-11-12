""" smashlib.ipy_venv

    Defines the ipy_venv extensions, which (usually) allows dynamically
    switching virtualenv's without leaving your shell.  Things are going
    to get hairy if you're using multiple python distributions.
"""
import inspect
import os, sys, glob

from IPython.utils.traitlets import Bool
from IPython.core.magic import Magics, magics_class, line_magic

from goulash.util import summarize_fpath
from smashlib.data import SMASH_DIR
from smashlib.v2 import Reporter

from smashlib.python import opj, ope, abspath, expanduser
from smashlib.util.events import receives_event
from smashlib.util import get_smash

from goulash.venv import get_venv, is_venv, to_vbin, to_vlib, get_path

# channel names for use with the smash bus
C_POST_ACTIVATE = 'post_activate_venv'
C_PRE_ACTIVATE = 'pre_activate_venv'
C_POST_DEACTIVATE = 'post_deactivate_venv'
C_PRE_DEACTIVATE = 'pre_deactivate'

@magics_class
class VirtualEnvMagics(Magics):
    @line_magic
    def venv_activate(self, parameter_s=''):
        self.report("venv_activate: "+parameter_s)
        self.vext.activate(parameter_s)

    @line_magic
    def venv_deactivate(self, parameter_s=''):
        self.vext.deactivate()

    @property
    def report(self):
        return self.vext.report


class VirtualEnvSupport(Reporter):

    def deactivate(self):
        try:
            venv = get_venv()
        except KeyError:
            self.warning("no venv to deactivate")
            return False
        else:
            if not venv:
                return False
            self.report("venv_deactivate: "+venv)
            self.publish(C_PRE_DEACTIVATE, venv)

            if not ope(venv):
                self.warning('refusing to deactivate (relocated?) venv')
                return #raise RuntimeError(err)

            del os.environ['VIRTUAL_ENV']
            path = get_path()
            path = path.split(':')

            # clean $PATH according to bash..
            # TODO: also rehash?
            vbin = to_vbin(venv)
            if vbin in path:
                msg = 'removing old venv bin from PATH: ' + \
                      summarize_fpath(str(vbin))
                self.report(msg)
                path.remove(vbin)
                os.environ['PATH'] = ':'.join(path)

            # clean sys.path according to python..
            # stupid, but this seems to work
            self.report('cleaning sys.path')
            new_path = []
            for entry in sys.path:
                if entry and not entry.startswith(venv):
                    new_path.append(entry)
                elif entry:
                    self.report(" del: "+summarize_fpath(entry))
            sys.path = new_path

            self._clean_user_namespace(venv)
            # TODO: clean sys.modules?
            self.publish(C_POST_DEACTIVATE, venv)
            return True

    def _clean_user_namespace(self, venv):
            """ clean ipython username to remove old project's code
                TODO: document and refactor
            """
            self.report("cleaning user namespace")
            names = []
            pm = get_smash().project_manager
            pdir = pm._current_project and pm.project_map[pm._current_project]
            namespace = get_smash().shell.user_ns
            for name,obj in namespace.items():
                try:
                    fname = inspect.getfile(obj)
                except TypeError:
                    # happens for anything that's not a module, class
                    # method, function, traceback, frame or code object
                    fname = None
                if fname:
                    test = fname.startswith(venv)
                    if pdir is not None:
                        test = test or fname.startswith(pdir)
                    if test and \
                        not name.startswith('_') and \
                        not name.startswith(SMASH_DIR):
                        names.append(name)
            for name in names:
                del self.smash.shell.user_ns[name]
            self.report("wiped from namespace: {0}".format(names))

    def activate(self, path):
        self.deactivate()
        absfpath = abspath(expanduser(path))
        self.smash.bus.publish(C_PRE_ACTIVATE, name=absfpath)
        if True:
            vbin = to_vbin(absfpath)
            vlib = to_vlib(absfpath)

            # compute e.g. <venv>/lib/python2.6.
            # we call bullshit if they have a more than one dir;
            # it might be a chroot but i dont think it's a venv
            python_dir = glob.glob(opj(vlib, 'python*/'))
            if len(python_dir)==0:
                raise RuntimeError('no python dir in {0}'.format(vlib))
            if len(python_dir) > 1:
                err = "multiple python dirs matching in {0}".format(vlib)
                raise RuntimeError(err)
            python_dir = python_dir[0]

            # this bit enables switching between two venv's
            # that might be "no-global-site" vs "use-global-site"
            site_file = opj(python_dir, 'site.py')
            assert ope(site_file)
            tmp = dict(__file__=site_file)
            execfile(site_file, tmp)
            tmp['main']()

            # some environment variable manipulation that would
            # normally be done by 'source bin/activate', but is
            # not handled by activate_this.py
            path = get_path().split(':')
            os.environ['VIRTUAL_ENV'] = absfpath
            msg = '$PATH was adjusted; rehashing aliases'
            self.report(msg)
            sandbox = dict(__file__ = opj(vbin, 'activate_this.py'))
            execfile(opj(vbin, 'activate_this.py'), sandbox)

            # libraries like 'datetime' can fail on import if this isnt done,
            # i'm not sure why activate_this.py doesnt accomplish it.
            dynload = opj(python_dir, 'lib-dynload')
            sys.path.append(dynload)

            # NB: this updates bins but kills other aliases!
            self.shell.magic('rehashx')
            self.smash.bus.publish(C_POST_ACTIVATE, absfpath)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    venv = VirtualEnvSupport(ip)
    VirtualEnvMagics.vext = venv
    ip.register_magics(VirtualEnvMagics)
    return venv


def unload_ipython_extension(ip):
    """undo magic here.."""
    print 'not implemented yet'
