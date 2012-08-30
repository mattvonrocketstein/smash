""" ipy_project_manager

    abstractions for project management
 """
import demjson
from collections import defaultdict
from smash.util import colorize, post_hook_for_magic, report
from smash.venv import VenvMixin

DEFAULT_CONFIG_SCHEMA = dict()


class Project(VenvMixin):
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
        self.being_watched = False

    def __repr__(self):
        """ """
        return 'project: ' + self.name

    @property
    def config(self):
        try:
            with open(self.config_file,'r') as fhandle:
                return demjson.decode(fhandle.read())
        except OSError:
            return DEFAULT_CONFIG_SCHEMA

    def shutdown(self):
        """ NB: this method will be used as an ipython hook """
        self.report('shutting down')
        [ x.stop() for x in self.watchlist ]
        #raise ipapi.TryNext()

    def _announce_if_project(self):
        """ post-hook for ipython's magic "cd"

            this function will notice when you change directories
            into a place that is registered as a project.
        """
        _dir = os.getcwd()
        if _dir in self._paths:
            m2 = ('This directory is also a registered project.'
                  '  You can activate it with "proj.activate(proj.{name})"')
            m2 = m2.format(name=os.path.split(_dir)[1])
            #self.report(m1);
            self.report(m2)

    def pre_activate(self, name, f):
        """ """
        self._pre_invokage[name] += [f]

    @classmethod
    def bind(kls, _dir, name=None, post_activate=[], post_invoke=[]):
        """ named alias for changing directory to "_dir". """
        _dir = os.path.os.path.expanduser(_dir)
        if name is None:
            name=os.path.split(_dir)[1]
        if not isinstance(post_invoke, list):
            post_invoke=[post_invoke]
        if not isinstance(post_activate, list):
            post_activate=[post_activate]
        kls._post_activate[name] += post_activate
        p = Project(name)
        p.dir = _dir
        kls._paths[name] = _dir

        @property
        def invoke(self):
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

            [ f() for f in self._post_invokage[name] + post_invoke ]
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
        N=0
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
            import fnmatch
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
(stolen) Implementation of the command-line I{pyflakes} tool.
"""

import compiler, sys
import os

checker = __import__('pyflakes.checker').checker

def check(codeString, filename):
    """
    Check the Python source given by C{codeString} for flakes.

    @param codeString: The Python source to check.
    @type codeString: C{str}

    @param filename: The name of the file the source came from, used to report
        errors.
    @type filename: C{str}

    @return: The number of warnings emitted.
    @rtype: C{int}
    """
    # Since compiler.parse does not reliably report syntax errors, use the
    # built in compiler first to detect those.
    try:
        try:
            compile(codeString, filename, "exec")
        except MemoryError:
            # Python 2.4 will raise MemoryError if the source can't be
            # decoded.
            if sys.version_info[:2] == (2, 4):
                raise SyntaxError(None)
            raise
    except (SyntaxError, IndentationError), value:
        msg = value.args[0]

        (lineno, offset, text) = value.lineno, value.offset, value.text

        # If there's an encoding problem with the file, the text is None.
        if text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            print >> sys.stderr, "%s: problem decoding source" % (filename, )
        else:
            line = text.splitlines()[-1]

            if offset is not None:
                offset = offset - (len(text) - len(line))

            print >> sys.stderr, '%s:%d: %s' % (filename, lineno, msg)
            print >> sys.stderr, line

            if offset is not None:
                print >> sys.stderr, " " * offset, "^"

        return 1
    except UnicodeError, msg:
        print >> sys.stderr, 'encoding error at %r: %s' % (filename, msg)
        return 1
    else:
        # Okay, it's syntactically valid.  Now parse it into an ast and check
        # it.
        tree = compiler.parse(codeString)
        w = checker.Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        return w.messages
        #for warning in w.messages:
        #    print warning
        #return len(w.messages)

def checkPath(filename):
    """
    Check the given path, printing out any warnings detected.

    @return: the number of warnings printed
    """
    try:
        fd = file(filename, 'U')
        try:
            return check(fd.read(), filename)
        finally:
            fd.close()
    except IOError, msg:
        print >> sys.stderr, "%s: %s" % (filename, msg.args[1])
        return 1

def smash_install():
    """
    TODO: CLEANR this part should not be in this file!
    """
    # build the manager.
    manager = Project('__main__')

    # consider every directory in ~/code to be a "project"
    # by default proj.<dir-name> simply changes into that
    instructions = [ [ 'bind_all',   ('~/code',),            {}],
                     [ 'bind',       ('~/jellydoughnut',),   {}], ]
    for method_name,args,kargs in instructions:
        getattr(manager,method_name)(*args, **kargs)

    # you can add activation hooks for things like
    # "start venv if present" or "show fab commands if present"
    from medley_ipy import load_medley_customizations
    from medley_ipy import load_medley_customizations2
    manager.bind_all('~/devel',
                     post_activate=load_medley_customizations2,
                     post_invoke=load_medley_customizations,)

    # add option parsing for project-manager
    from smash.parser import SmashParser
    SmashParser.defer_option(args=('-p', "--project",),
                                   kargs=dict(
                                       dest="project", default='',
                                       help="specify a project to initialize", ),
                                   handler = lambda opts: getattr(manager, opts.project).activate)


    # install hooks in the environment
    post_hook_for_magic('cd', manager._announce_if_project)
    __IPYTHON__.shell.user_ns['proj'] = manager
    __IPYTHON__.hooks['shutdown_hook'].add(lambda: manager.shutdown())
    __IPYTHON__.hooks['pre_prompt_hook'].add(manager.check)
