""" ipy_project_manager

    abstractions for project management
 """
import os
import demjson
import fnmatch
from collections import defaultdict

from smash.python import opd, opj, expanduser
from smash.reflect import namedAny
from smash.util import colorize, post_hook_for_magic, report
from smash.venv import VenvMixin

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

CONFIG_FILE_NAME = 'projects.json'

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

    def _announce_if_project(self):
        """ post-hook for ipython's magic "cd"

            this function will notice when you change directories
            into a place that is registered as a project.
        """
        _dir = os.getcwd()
        if _dir in self._paths:
            m2 = ('This directory is also a registered project. '
                  ' You can activate it with "proj.activate(proj.{name})"')
            m2 = m2.format(name=os.path.split(_dir)[1])
            self.report(m2)

    @property
    def aliases(self):
        from smash.aliases import Aliases
        aliases = self._config.get('aliases', {})
        local_aliases = aliases.get(self.name, [])
        out = Aliases()
        [ out.add(alias, self.name) for alias in local_aliases ]
        return out

    @classmethod
    def bind(kls, _dir, name=None, post_activate=[], post_invoke=[]):
        """ named alias for changing directory to "_dir". """
        _dir = expanduser(_dir)
        if name is None:
            name = os.path.split(_dir)[1]
        if not isinstance(post_invoke, list):   post_invoke   = [ post_invoke ]
        if not isinstance(post_activate, list): post_activate = [ post_activate ]

        tmp = []
        for x in post_activate:
            x = namedAny(x) if isinstance(x, (str, unicode)) else x
            tmp.append(x)
        post_activate = tmp

        tmp = []
        for x in post_invoke:
            x = namedAny(x) if isinstance(x, (str, unicode)) else x
            tmp.append(x)
        post_invoke = tmp

        kls._post_activate[name] += post_activate
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
            self.report(str(self.msgs))
        return ''

    def watch(self):
        """ """
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

def _smash_install():
    """
    TODO: CLEANR this part should not be in this file!
    """
    config_file = opj(opd(opd(__file__)), CONFIG_FILE_NAME)
    Project._config_file = config_file
    report.project_manager('loading config: ' + config_file)
    if not os.path.exists(config_file):
        config = {}
        report.project_manager(' file does not exist')
    else:
        config = demjson.decode(open(config_file,'r').read())
        report.project_manager(' config keys: '+str(config.keys()))
    manager = Project(ROOT_PROJECT_NAME)

    # dont move this next line.  post_activate/post_invoke things might want the manager.
    __IPYTHON__.shell.user_ns['proj'] = manager

    manager._config = config
    instructions = config.get('instructions', [])
    # consider every directory in ~/code to be a "project"
    # by default proj.<dir-name> simply changes into that
    for method_name, args, kargs in instructions:
        getattr(manager, method_name)(*args, **kargs)

    # add option parsing for project-manager
    from smash.parser import SmashParser
    SmashParser.defer_option(args=('-p', "--project",),
                                   kargs=dict(
                                       dest="project", default='',
                                       help="specify a project to initialize", ),
                                   handler = lambda opts: getattr(manager,
                                                                  opts.project).activate)

    # per-project aliases
    default_aliases = config.get('aliases', {}).get(ROOT_PROJECT_NAME, [])
    from smash import aliases
    default_aliases = [ aliases.add(alias) for alias in default_aliases ]
    report.project_manager('adding aliases: ' + str(default_aliases))
    aliases.install()

    #raise Exception, aliases
    # install hooks in the environment
    # FIXME: this stopped working
    post_hook_for_magic('cd', manager._announce_if_project)

    __IPYTHON__.hooks['shutdown_hook'].add(lambda: manager.shutdown())
    __IPYTHON__.hooks['pre_prompt_hook'].add(manager.check)

from smash.plugins import SmashPlugin
class Plugin(SmashPlugin):
    def install(self):
        _smash_install()
