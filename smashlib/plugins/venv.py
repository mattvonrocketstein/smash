""" smashlib.plugins.venv

    Defines the venv extension, which (usually) allows dynamically
    switching between virtualenv's with usual side effects in the
    shell environment, the executable path, the module path, and the
    python namespace.. all without leaving your shell.

    Caveats: This approach works pretty well and is mostly unsurprising,
    but, things are going to get hairy if you're using multiple python
    distributions in multiple venv's, and if you're mixing global/nonglobal
    options for the virtualenv "use site env".

    Additionally, the plugin will set up tab completion over virtualenv
    the usual command line options.
"""
import inspect
import os
import sys
import glob

from IPython.core.magic import Magics, magics_class, line_magic

from goulash._os import summarize_fpath
from goulash.venv import get_venv, to_vbin, to_vlib, get_path

from smashlib import get_smash
from smashlib.plugins import Plugin
from smashlib.data import SMASH_DIR
from goulash.python import opj, ope, abspath, expanduser
from smashlib.completion import opt_completer
from smashlib._logging import smash_log


# "real_prefix" is set by virtualenv itself. this
# is interesting but maybe not as useful as i thought
REAL_PREFIX = getattr(sys, 'real_prefix', sys.prefix)

from smashlib.channels import (
    C_POST_ACTIVATE, C_PRE_ACTIVATE,
    C_POST_DEACTIVATE, C_PRE_DEACTIVATE)


@magics_class
class VirtualEnvMagics(Magics):

    @line_magic
    def venv_activate(self, parameter_s=''):
        msg = "venv_activate: " + parameter_s
        smash_log.info(msg)
        self.report(msg)
        self.vext.activate(parameter_s)

    @line_magic
    def venv_deactivate(self, parameter_s=''):
        self.vext.deactivate()

    @property
    def report(self):
        return self.vext.report


virtualenv_completer = opt_completer('virtualenv')


class VirtualEnvSupport(Plugin):
    sys_path_changes = []

    def deactivate(self):
        try:
            venv = get_venv()
        except KeyError:
            self.warning("no venv to deactivate")
            return False
        else:
            if not venv:
                return False
            self.report("venv_deactivate: " + venv)
            self.publish(C_PRE_DEACTIVATE, venv)

            if not ope(venv):
                self.warning('refusing to deactivate (relocated?) venv')
                return  # raise RuntimeError(err)

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
            msg = 'clean sys.path'  # ,sys.path_changes)
            self.report(msg)
            smash_log.info(msg)
            reset_path = getattr(self, 'reset_path', None)
            if reset_path is not None:
                msg = str(set(sys.path) ^ set(reset_path))
                msg = 'sys.path difference: {0}'.format(msg)
                self.report(msg)
                smash_log.debug(msg)
                sys.path = reset_path
                self.reset_path = sys.path
            else:
                self.reset_path = sys.path
            self._clean_user_namespace(venv)
            self.publish(C_POST_DEACTIVATE, venv)
            return True

    def _clean_user_namespace(self, venv):
        """ clean ipython username to remove old project's code
            TODO: document and refactor
        """
        msg = "cleaning user namespace"
        smash_log.info(msg)
        self.report(msg)
        names = []
        pm = get_smash().project_manager
        pdir = pm._current_project and pm.project_map[pm._current_project]
        namespace = get_smash().shell.user_ns
        for name, obj in namespace.items():
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
        if names:
            self.report("wiped from namespace: {0}".format(names))

    def activate(self, path):
        self.deactivate()
        #old_sys_path = [x for x in sys.path]
        self._activate(path)
        #sys.path_changes = set(sys.path) - set(old_sys_path)
        # print 'that added',sys.path_changes

    def _activate(self, path):
        absfpath = abspath(expanduser(path))
        self.publish(C_PRE_ACTIVATE, name=absfpath)
        if True:
            vbin = to_vbin(absfpath)
            vlib = to_vlib(absfpath)

            # compute e.g. <venv>/lib/python2.6.
            # we call bullshit if they have a more than one dir;
            # it might be a chroot but i dont think it's a venv
            python_dir = glob.glob(opj(vlib, 'python*/'))
            if len(python_dir) == 0:
                raise RuntimeError('no python dir in {0}'.format(vlib))
            if len(python_dir) > 1:
                err = "multiple python dirs matching in {0}".format(vlib)
                raise RuntimeError(err)
            python_dir = python_dir[0]

            # this bit might enable switching between two venv's
            # that are be "no-global-site" vs "use-global-site"
            # .. tabling it for now
            # site_file = opj(python_dir, 'site.py')
            # assert ope(site_file)
            # tmp = dict(__file__=site_file)
            # execfile(site_file, tmp)
            #  tmp['main']()

            # some environment variable manipulation that would
            # normally be done by 'source bin/activate', but is
            # not handled by activate_this.py
            #path = get_path().split(':')
            os.environ['VIRTUAL_ENV'] = absfpath

            sandbox = dict(__file__=opj(vbin, 'activate_this.py'))
            execfile(opj(vbin, 'activate_this.py'), sandbox)
            self.reset_path = sandbox['prev_sys_path']

            # libraries like 'datetime' can very occasionally fail on import
            # if this isnt done, and i'm not sure why activate_this.py doesnt
            # accomplish it.  it might have something to do with venv's using
            # mixed pythons (different versions) or mixed --no-site-packages
            # tabling it for now
            # dynload = opj(python_dir, 'lib-dynload')
            # sys.path.append(dynload)

            # NB: this rehash will update bins but iirc kills aliases!
            msg = '$PATH was adjusted to {0}'.format(os.environ['PATH'])
            smash_log.debug(msg)
            self.report('Adjusting $PATH')
            msg = 'rehashing aliases'
            smash_log.info(msg)
            self.shell.magic('rehashx')
            self.publish(C_POST_ACTIVATE, absfpath)


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    venv = VirtualEnvSupport(ip)
    VirtualEnvMagics.vext = venv
    ip.register_magics(VirtualEnvMagics)
    get_smash().add_completer(virtualenv_completer, re_key='virtualenv .*')
    return venv


def unload_ipython_extension(ip):
    """undo magic here.."""
    print 'not implemented yet'
