""" smashlib.projects
"""

import os

from collections import defaultdict

from smashlib.python import expanduser
from smashlib.reflect import namedAny
from smashlib.util import colorize, report, list2table
from smashlib.util import truncate_fpath
from smashlib.venv import VenvMixin, _contains_venv
from smashlib.util import report

COMMAND_NAME = 'proj'
ROOT_PROJECT_NAME = '__smash__'

def which_vcs(fpath):
    import vcs
    try:
        return vcs.get_repo(fpath).__class__.__name__
    except vcs.VCSError:
        return 'N/A'

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
        return header,dat

    @property
    def __doc__(self):
        header, dat = self._doc_helper(self._paths)
        return """Projects:\n\n""" + list2table(dat, header=header)

    @property
    def CURRENT_PROJECT(self):
        """ FIXME: makes no distinction for whether it's activated, though """
        _dir = os.getcwd()
        _venv = os.environ.get('VIRTUAL_ENV')
        for name,path in self._paths.items():
            if _venv and _venv.startswith(path): return name
            if path == _dir: return name
        return None

    def __init__(self, name):
        """ """
        self.name = name
        self._pre_invokage  = defaultdict(lambda: [])
        self._post_invokage = defaultdict(lambda: [])

    @property
    def watched(self):
        return self._config.get('watchdog',{}).get(self.name,{})

    def __repr__(self):
        return 'project: ' + self.name

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

    """ @property
    def aliases(self):
        from smashlib import ALIASES as aliases
        aliases = self._config.get('aliases', {})
        local_aliases = aliases.get(self.name, [])
        out = Aliases()
        [ aliases.add(alias, self.name) for alias in local_aliases ]
        return out"""

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
                    func.__doc__ = 'post-activation command for {0}\n\n:{1}'.format(name, x)

                # FIXME: ugly and special-cased because __IPY__.system() doesnt work
                elif x.startswith('cd'):
                    dname = x.split()[-1]
                    func = lambda: os.chdir(dname)
                    func.__doc__ = 'post-activation command for {0}\n\n:os.chdir(\'{1}\')'.format(name, dname)

                else:
                    func = namedAny(x)
            else:
                raise Exception,'niy: ' + str(x)

            if func not in kls._post_activate[name]:
                kls._post_activate[name] += [func]

    @classmethod
    def bind(kls, _dir, name=None, post_activate=[], post_invoke=[]):
        """ installs a named alias for changing directory to "_dir". """

        _dir = expanduser(_dir)
        if name is None:
            name = os.path.split(_dir)[1]
        if not isinstance(post_invoke, list):   post_invoke   = [ post_invoke   ]
        kls._add_post_activate(name, post_activate)

        tmp = []
        for x in post_invoke:
            x = namedAny(x) if isinstance(x, (str, unicode)) else x
            tmp.append(x)
        post_invoke = tmp


        kls._paths[name] = _dir

        @property
        def invoke(self):
            """ FIXME: yeah this is a pretty awful hack..
            """
            from smashlib import ALIASES as aliases
            if self.CURRENT_PROJECT:
                old_aliases = aliases[self.CURRENT_PROJECT]
                count = [ aliases.uninstall(a) for a in old_aliases ]
                if count:
                    self.report("removed {0} aliases from the previous project".format(len(count)))

            new_aliases = self._config.get('aliases',{}).get(name,[])
            [ aliases.add(a, name) for a in new_aliases]
            p = Project(name)
            p.dir = _dir
            p._config = self._config
            [ f() for f in self._pre_invokage[name] ]
            os.chdir(p.dir)
            [ f() for f in self._post_invokage[name] + post_invoke ]
            return p

        setattr(kls, name, invoke)

    @classmethod
    def report(kls, *args):
        """ FIXME: use default smash report """
        report(*args)#if len(args)>1: print colorize('{red}project-manager:{normal}'),args
        #else: report.project_manager(args[0])

    @classmethod
    def bind_all(kls, _dir, **kargs):
        """ binds every directory in _dir as a project """
        N = 0
        _dir = os.path.expanduser(_dir)
        if not os.path.exists(_dir):
            # FIXME: make this red
            msg = 'ERROR: cannot bind nonexistant directory @ "{0}"'
            report(msg.format(_dir))
            return
        listing = os.listdir(_dir)
        for name in listing:
            tmp = os.path.join(_dir,name)
            if os.path.isdir(tmp):
                N += 1
                kls.bind(tmp, name, **kargs)
        report('binding ' + _dir + ' (' + str(N) + ' projects found)')

    def check(self):
        if self.msgs:
            msg = self.msgs.pop()
            report(msg)
        return None

    def watch(self):
        """ TODO: fix / refactor """
        if self.being_watched:
            self.being_watched.stop()
            self.watchlist.remove(self.being_watched)
            report('watch stopped')
            return
        try:
            import pyinotify
        except ImportError:
            report("Could not import pyinotify.  You'll need to install "
                        "it system wide, or activate a venv where it is already "
                        "installed")
            return
        else:
            report("starting watch")
            _dir = self.dir
            """
            class EventHandler(pyinotify.ProcessEvent):
                #def process_IN_CREATE(himself, event):
                #def process_default(himself, event):
                def base(himself, *ars):
                    self.report('testing')

                def process_IN_MODIFY(himself, event):
                    if fnmatch.fnmatch(event.pathname, '*.py'):
                        clean = [[type(x).__name__,x] for x in checkPath(event.pathname)]
                        clean = [ x[1] for x in clean if not x[0].startswith('Unused') ]
                        for msg in clean:
                            self.msgs.append(str(msg))



            mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
            wm = pyinotify.WatchManager()
            wm.add_watch(_dir, mask, rec=1)
            notifier = pyinotify.ThreadedNotifier(wm, default_proc_fun=EventHandler())
            self.being_watched = notifier
            self.watchlist.append(self.being_watched)
            notifier.start()
            self.notifiers += [notifier]
            """
