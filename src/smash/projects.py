""" smash.projects
"""

import os

from collections import defaultdict
from smash.python import expanduser
from smash.reflect import namedAny
from smash.util import colorize, report
from smash.venv import VenvMixin

COMMAND_NAME = 'proj'
ROOT_PROJECT_NAME = '__smash__'

DEFAULT_CONFIG_SCHEMA = dict(
    # schema:
    #   { 'project_name' : ['alias_cmd real --command goes_here', .. ] }
    aliases = dict(

        # __smash__ holds generic, "always-on" kinds of aliases which will
        # take effect regardless of what project is the active one
        __smash__ = []

        ),

    # FIXME: document schema based on config/example_project.json
    instructions = [],

    )

class Hooks(object):

    def shutdown(self):
        """ NB: this method will be used as an ipython hook """
        self.report('shutting down')
        [ x.stop() for x in self.watchlist ]
        #raise ipapi.TryNext()

    def pre_activate(self, name, f):
        """ FIXME: cumbersome """
        self._pre_invokage[name] += [f]

class Project(VenvMixin, Hooks):
    """ class for holding Project abstractions. in the simplest case,
        beginning work on on a project just means changing directories.
        you can also work with python virtual environments like this:

        >>> proj._activate(proj.project_name)
        >>> proj.project_name.activate()

        TODO: document difference between project "invoking" vs "activation"
        TODO: should really rename to 'projectman' or something
    """
    msgs      = []
    watchlist = []
    dir       = None
    _paths    = {}
    notifiers = []
    _post_activate = defaultdict(lambda: [])

    def __init__(self, name):
        """ """
        self.name = name
        self._pre_invokage  = defaultdict(lambda: [])
        self._post_invokage = defaultdict(lambda: [])
        self.being_watched  = False

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
        #report('yo')
        _dir = os.getcwd()
        if _dir in self._paths.values():
            m2 = ('This directory is also a registered project. '
                  ' You can activate it with "proj.activate(proj.{name})"')
            m2 = m2.format(name=os.path.split(_dir)[1])
            self.report(m2)

    @property
    def aliases(self):
        """ """
        from smash.aliases import Aliases
        aliases = self._config.get('aliases', {})
        local_aliases = aliases.get(self.name, [])
        out = Aliases()
        [ out.add(alias, self.name) for alias in local_aliases ]
        return out

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
                item = x
            elif isinstance(x, basestring):
                #kls._post_activate[name] += post_activate
                if x.startswith('$'):
                    def item():
                        os.system(x[1:])
                    item.__doc__ = 'post-activation command for {0}\n\n:{1}'.format(name,x)

                # FIXME: ugly and special-cased because __IPY__.system() doesnt work
                elif x.startswith('cd'):
                    dname = x.split()[-1]
                    def item():
                        os.chdir(dname)
                    item.__doc__ = 'post-activation command for {0}\n\n:os.chdir(\'{1}\')'.format(name, dname)

                else:
                    item = namedAny(x)
            else:
                raise Exception,'niy: ' + str(x)

            if item not in kls._post_activate[name]:
                kls._post_activate[name] += [item]

    @classmethod
    def bind(kls, _dir, name=None, post_activate=[], post_invoke=[]):
        """ installs a named alias for changing directory to "_dir". """
        _dir = expanduser(_dir)
        if name is None:
            name = os.path.split(_dir)[1]
        if not isinstance(post_invoke, list):   post_invoke   = [ post_invoke   ]
        #if not isinstance(post_activate, list): post_activate = [ post_activate ]

        kls._add_post_activate(name, post_activate)
        #tmp = []
        #for x in post_activate:
        #    x = namedAny(x) if isinstance(x, (str, unicode)) else x
        #    tmp.append(x)
        #post_activate = tmp
        #kls._post_activate[name] += post_activate

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
            p = Project(name)
            p.dir = _dir
            p._config = self._config
            [ f() for f in self._pre_invokage[name] ]
            os.chdir(p.dir)
            [ f() for f in self._post_invokage[name] + post_invoke ]
            p.aliases.install()
            return p

        setattr(kls, name, invoke)

    @classmethod
    def report(kls, *args):
        """ FIXME: use default smash report """
        if len(args)>1: print colorize('{red}project-manager:{normal}'),args
        else: print colorize('{red}project-manager:{normal} ') + args[0]

    @classmethod
    def bind_all(kls, _dir, **kargs):
        """ binds every directory in _dir as a project """
        N = 0
        _dir = os.path.expanduser(_dir)
        for name in os.listdir(_dir):
            tmp = os.path.join(_dir,name)
            if os.path.isdir(tmp):
                N += 1
                kls.bind(tmp, name, **kargs)
        kls.report('binding ' + _dir + ' (' + str(N) + ' projects found)')

    def check(self):
        if self.msgs:
            msg = self.msgs.pop()
            self.report(msg)
        return ''

    def watch(self):
        """ TODO: fix / refactor """
        if self.being_watched:
            self.being_watched.stop()
            self.watchlist.remove(self.being_watched)
            self.report('watch stopped')
            return
        try:
            import pyinotify
        except ImportError:
            self.report("Could not import pyinotify.  You'll need to install "
                        "it system wide, or activate a venv where it is already "
                        "installed")
            return
        else:
            self.report("starting watch")
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
