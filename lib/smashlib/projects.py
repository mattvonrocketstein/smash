""" smashlib.projects
"""
import os
from collections import defaultdict

import smashlib
from smashlib.bus import bus
from smashlib.python import ope, expanduser, listdir, isdir
from smashlib.reflect import namedAny, ObjectNotFound
from smashlib.venv import VenvMixin, _contains_venv, get_venv
from smashlib.util import (\
    report, which_vcs, colorize,
    report, list2table, truncate_fpath)
from smashlib.aliases import (\
    kill_old_aliases, add_new_aliases,
    rehash_aliases)

NO_ACTIVE_PROJECT = '__not_set__'
COMMAND_NAME = 'proj'
ROOT_PROJECT_NAME = '__smash__'

class Hooks(object):

    def shutdown(self):
        """ NB: this method will be used as an ipython hook """
        report.project_manager('shutting down')
        [ x.stop() for x in self.watchlist ]
        #raise ipapi.TryNext()

class Project(VenvMixin, Hooks):
    #   class for holding Project abstractions. in the simplest case,
    #   beginning work on on a project just means changing directories.
    #   you can also work with python virtual environments like this:
    #
    #   >>> proj._activate(proj.project_name)
    #   >>> proj.project_name.activate()
    #
    #   TODO: document difference between project "invoking" vs "activation"
    #   TODO: should really rename to 'projectman' or something
    CURRENT_PROJECT = NO_ACTIVE_PROJECT
    msgs      = []
    watchlist = []
    dir       = None
    _paths    = {}
    notifiers = []
    _post_activate = defaultdict(lambda: [])

    def _doc_helper(self, path_subset):
        dat = []
        for x in path_subset:
            fpath         = self._paths[x]
            trunc_fpath   = truncate_fpath(fpath) # ~ replace
            contains_venv = _contains_venv(fpath) or 'N/A'
            contains_venv = contains_venv.replace(fpath,'.')
            vcs = which_vcs(fpath)
            dat.append([x, trunc_fpath, contains_venv, vcs])
        header = ['name', 'path', 'virtualenv', 'vcs']
        return header, dat

    def __qmark__(self):
        header, dat = self._doc_helper(self._paths)
        hdr = "{red}SmaSh Project-Manager{normal}"
        _help = ["\n\tconfig-file: {red}" +self._config_file + "{normal}",
                 "for summary of available projects type: {red}proj.summary{normal}",
                 "to cd to a project's home-dir type: {red}proj.project_name{normal}",
                 "to activate a project type: {red}proj.project_name.activate{normal}",
                 ]
        _help = '\n\t'.join(_help)
        report(hdr + _help)

    def __init__(self, name):
        """ """
        self.name = name
        self._pre_invokage  = defaultdict(lambda: [])
        self._post_invokage = defaultdict(lambda: [])
        bus.subscribe('pre_activate', kill_old_aliases)
        bus.subscribe('post_activate', add_new_aliases)
        bus.subscribe('post_activate', rehash_aliases)

    @property
    def watched(self):
        return self._config.get('watchdog',{}).get(self.name,{})

    def __repr__(self):
        return 'Project("{0}")'.format(self.name)

    @property
    def _active_project(self):
        tmp = [x for x in self._paths if self._paths[x]==os.getcwd()]
        if tmp: return tmp[0]

    def _announce_if_project(self):
        """ post-hook for ipython's magic "cd"

            this function will notice when you change directories
            into a place that is registered as a project.
        """
        _dir = os.getcwd()
        if _dir in self._paths.values():
            report('This directory is also a project. ')
            cmd = '"{CMD}.activate(proj.{name})"'.format(CMD=COMMAND_NAME,
                                                         name=os.path.split(_dir)[1])
            report('  To activate it: '+cmd)

    @classmethod
    def _add_post_activate(kls, name, something):
        """ adds activation-action `something` for project named `name`.

            `something` can be a function, a python dotpath that resolves to function,
            or if it starts with '$' will be interpretted as shell code.

        """
        if not isinstance(something, (list, tuple) ):
            something = [ something ]
        for x in something:
            if callable(x):
                func = x
            elif isinstance(x, basestring):
                if x.startswith('$'):
                    func = lambda: os.system(x[1:])
                    tmp = 'post-activation command for {0}\n\n:{1}'
                    tmp = tmp.format(name, x)
                    func.__doc__ = tmp

                # FIXME: ugly and special-cased because __IPY__.system() doesnt work
                elif x.startswith('cd'):
                    dname = x.split()[-1]
                    func = lambda: os.chdir(dname)
                    tmp = 'post-activation command for {0}\n\n:os.chdir(\'{1}\')'
                    tmp = tmp.format(name, dname)
                    func.__doc__ = tmp
                else:
                    try:
                        func = namedAny(x)
                    except ObjectNotFound,e:
                        report("There is an error in your configuration "
                               "file.  Could not import name \"{0}\"".format(x))
                        return
            else:
                raise Exception,('post-activation entries should be callable'
                                 ' or strings that point to callables: ') + str(x)
            bus.subscribe('post_activate.'+name, func)
            if func not in kls._post_activate[name]:
                kls._post_activate[name] += [func]
    @property
    def files(self):
        """ TODO: refactor, probably allow globbing """
        return [x.strip() for x in os.popen('find '+self.dir).readlines()]

    _proj_cache = {}

    @classmethod
    def get_proj(kls, name):
        return kls._proj_cache.get(name, None)

    @classmethod
    def bind(kls, _dir, name=None, post_activate=[], post_invoke=[]):
        """ installs a named alias for changing directory to "_dir". """
        _dir = expanduser(_dir)
        if name is None:
            name = os.path.split(_dir)[1]

        if not isinstance(post_invoke, list):
            post_invoke   = [ post_invoke   ]
        kls._add_post_activate(name, post_activate)

        tmp = []
        for x in post_invoke:
            try:
                x = namedAny(x) if isinstance(x, (str, unicode)) else x
            except ObjectNotFound,e:
                report("There is an error in your configuration "
                       "file.  Could not import name \"{0}\"".format(x))
                return
            tmp.append(x)
            bus.subscribe('post_invoke.'+name, x)
        kls._paths[name] = _dir
        p = Project(name)#, config=self._config)
        p.dir = _dir
        kls._proj_cache[name] = p

        @property
        def invoke(self):
            """ FIXME: yeah this is a pretty awful hack.. """
            bus.publish('pre_invoke', name=name)
            from smashlib import ALIASES as aliases
            new_aliases = self._config.get('aliases', {}).get(name, [])
            [ aliases.add(a, name) for a in new_aliases]
            [ f() for f in self._pre_invokage[name] ]
            os.chdir(p.dir)
            bus.publish('post_invoke.' + name)
            return p

        setattr(kls, name.replace('-','_').replace('.','_'), invoke)

    def __getitem__(self, name):
        return name
        tmp = Project(name)
        #p.dir =
        return

    @classmethod
    def report(kls, *args):
        """ FIXME: use default smash report """
        report(*args)

    @classmethod
    def bind_all(kls, _dir, **kargs):
        """ binds every directory in _dir as a project """
        N = 0
        _dir = expanduser(_dir)
        if not ope(_dir):
            # FIXME: adding "WARNING" event to bus, make this red
            msg = '\tCannot bind nonexistant directory @ "{0}".  '
            msg = msg.format(_dir)
            bus.warning(msg)
            msg = '\tCheck your configuration @ "{0}".'
            msg = msg.format(smashlib._meta['project_config'])
            report.WARNING(msg)
            return
        listing = listdir(_dir)
        for name in listing:
            tmp = os.path.join(_dir, name)
            if isdir(tmp):
                N += 1
                kls.bind(tmp, name, **kargs)
        report.project_manager('binding {0} ({1} projects found)'.format(_dir,N))
