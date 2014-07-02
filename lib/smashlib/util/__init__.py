# -*- coding: utf-8
""" smashlib.util
"""
import os, sys, time
import StringIO, threading
import demjson, asciitable

from IPython import ipapi, ColorANSI

from smashlib.python import get_env, opd, ops, opj, ope, expanduser
from smashlib.util.text_proc import split_on_unquoted_semicolons, truncate_fpath

LATE_STARTUP_DELAY = 2

# TODO: use pygments here instead of IPython
TERM_COLORS = tc = ColorANSI.TermColors()

# NOTE: might be obsolete.  this was only needed if/when
#       using the "import all available modules" strategy
CONFLICTING_NAMES  = ('curl gc git time pwd pip pyflakes '
                      'easy_install virtualenv py').split()
def _user_ns():
    return __IPYTHON__.user_ns

def _ip():
    return ipapi.get()

#def bus():
#    """ get the main bus.  this is used instead of a direct import,
#        because the later may not be safe (depends on exactly when it's
#        called and how much of the bootstrap has already finished)
#    """
#    from smashlib import bus
#    return bus

def home():
    return get_env('HOME')

def add_hook(hook_name, new_hook, priority):
    hook_obj = getattr(__IPYTHON__.hooks, hook_name)
    return hook_obj.add(new_hook, priority)
def set_complete(func, key, **kargs):
    return _ip().set_hook('complete_command',
                          func, re_key=key, **kargs)
def set_editor(editor):
    _ip().options['editor'] = editor
    return editor

def do_it_later(func, delay=LATE_STARTUP_DELAY):
    """ HACK: yeah, this is ugly, but sometimes using the "late_startup_hook"
              ipython provides just doesnt work. cry me a river..
    """
    def tmp():
        time.sleep(1)
        func()
    threading.Thread(target=tmp).start()

def panic():
    ("kill ALL the running instances of smash.\n"
     "useful when you have a misbehaving plugin..")
    import psutil, os
    matches = [ x for x in psutil.process_iter() \
                if 'smash' in ' '.join(x.cmdline) ]
    proc = [ x for x in matches if x.pid==os.getpid() ][0]
    matches.remove(proc)
    [ m.kill() for m in matches ]
    proc.kill()

def read_config(config_file):
    """ TODO: parameter for wheter errors are fatal? """
    with open(config_file, 'r') as fhandle:
        try: config = demjson.decode(fhandle.read())
        except demjson.JSONDecodeError,e:
            err = "cannot continue, failed to read json file: " + config_file
            report.ERROR(err+'\n\n\t' + str(e))
            return die()
        return config

def replace_magic(original_magic_name, new_magic_function):
    """ """
    if not original_magic_name.startswith('magic_'):
        original_magic_name = 'magic_' + original_magic_name
    if not hasattr(__IPYTHON__, original_magic_name):
        raise RuntimeError('cannot replace magic that does not exist')
    setattr(__IPYTHON__, original_magic_name, new_magic_function)

def pre_magic(original_magic_name, parameter_s_mutator):
    """ mechanism for mutating parameters that go into magic functions
        before they are called.  for example, this is used so that
        editor.json can support "never_execute_code" (see smashlib.main)
    """
    if not original_magic_name.startswith('magic_'):
        original_magic_name = 'magic_' + original_magic_name
    old_magic = getattr(__IPYTHON__,original_magic_name)
    def new_magic(parameter_s, *args, **kargs):
        parameter_s = parameter_s_mutator(parameter_s)
        return old_magic(parameter_s, *args, **kargs)
    new_magic.__doc__ = old_magic.__doc__
    replace_magic(original_magic_name, new_magic)

def post_hook_for_magic(original_magic_name, new_func):
    """ attach a new post-run hook for an existing magic function """
    #print 'chaining',original_magic_name,new_func
    old_magic = getattr(__IPYTHON__, 'magic_' + original_magic_name)
    new_name = '_magic_{0}_chain'.format(original_magic_name)
    chain = getattr(__IPYTHON__, new_name, [])
    if not chain:
        def new_magic(self, parameter_s=''):
            out = old_magic(parameter_s=parameter_s)
            chain = getattr(__IPYTHON__, '_magic_{0}_chain'.format(original_magic_name), [])
            for f in chain:
                f()
            return out
        new_magic.__doc__=old_magic.__doc__
        _ip().expose_magic(original_magic_name, new_magic)
    chain += [new_func]
    setattr(__IPYTHON__, '_magic_{0}_chain'.format(original_magic_name), chain)

def clean_namespace():
    """ clean python namespace in a few places where it shadows unix,
        or in case it collides with the aliases we'll set up later """

    def wipe(name):
        if name in __IPYTHON__.shell.user_ns:
            del __IPYTHON__.shell.user_ns[name]

    [ wipe(x) for x in CONFLICTING_NAMES ]


def colorize(msg):
    """ """
    # .format() is not used because KeyError might happen
    # when using report(msg+str(some_dictionary))
    return msg.replace('{red}', tc.Red).replace('{normal}', tc.Normal)

class Reporter(object):
    """ syntactic sugar for reporting """
    def __init__(self, label=u'>>'):
        self.label = label

    def __getattr__(self, label):
        return self.__class__(label)

    def _report(self,msg):
        print colorize('{red}' + self.label + '{normal}: ' + msg)

    def _warn(self,msg):
        return self._report(msg)

    def __call__(self, msg):
        return self._report(msg)

class MaybeReport(Reporter):
    def _report(self, msg):
        from smashlib import VERBOSE
        if VERBOSE:
            super(MaybeReport,self)._report(msg)

report_if_verbose = MaybeReport()
report = Reporter()

def add_shutdown_hook(f):
    def newf(*args, **kargs):
        f(*args,**kargs)
        raise ipapi.TryNext()
    __IPYTHON__.hooks['shutdown_hook'].add(newf)

def die():
    """
    FIXME: this is horrible, but i remember thinking i had no choice..
    """
    threading.Thread(target = lambda: \
                     os.system('kill -KILL ' + str(os.getpid()))).start()

def list2table(dat, header=[], indent=''):
    """ using asciitable, this function can return
        strings of neatly formated tabular data
    """
    if header: dat = [header] + dat
    s = StringIO.StringIO()
    out = asciitable.write(dat, output=s, Writer=asciitable.FixedWidthNoHeader)
    s.seek(0)
    out = s.read()
    if header:
        out = out.split('\n')
        line1 = out[0]
        out.insert(1, '-'*len(line1))
        out = '\n'.join(out)
    if indent:
        out = out.split('\n')
        out = [ indent+line for line in out ]
        out = '\n'.join(out)
    return out

def this_project():
    """ returns current project object (not name) """
    from smashlib import PROJECTS as proj
    wd = os.getcwd()
    for name, path in proj._paths.items():
        if wd.startswith(path):
            return proj.get_proj(name)

def this_venv():
    import os
    from smashlib.util import do_it_later, truncate_fpath
    result = os.environ.get('VIRTUAL_ENV','')
    result = truncate_fpath(result)
    result = os.path.sep.join(result.split(os.path.sep)[-2:])
    return '({0})'.format(result)

def which_vcs(fpath):
    """ very primitive VCS detector.

        TODO: there are various pypi modules that will
              do this, but some are pretty big.  probably
              need to review the options a little before
              adding a dependency
    """
    try:
        files = os.listdir(fpath)
    except OSError:
        return "N/A"
    if '.svn' in files:
        # why doesnt vcs do this..
        return 'Subversion'
    elif '.git' in files:
        return 'git'
    else:
        return 'N/A'

def embed():
    """ DEPRECATED? """
    _smashlib, _smashplugins = (expanduser('~/.smash/'),
                                expanduser('~/.smash/plugins'))
    for p in [_smashlib,_smashplugins]:
        if p not in sys.path:
            sys.path.append(p)
    import smashlib
    from smashlib.embed import SmashEmbed
    SmashEmbed()()

get_last_line  = lambda: __IPYTHON__.user_ns['In'][-1]

class LastCommandHook(object):
    def __init__(self, fxn):
        self.fxn = fxn

    def __call__(self, *args, **kargs):
        last_line = get_last_line()
        sys_call_start = '_ip.system('
        if last_line.startswith(sys_call_start):
            # might be " or '.  TODO: regex
            quote_char = last_line[len(sys_call_start):][0]
            # get the thing inbetween the quotes
            sys_cmd = last_line.split(quote_char)[1]
            sys_cmd = sys_cmd.strip()
            self.fxn(sys_cmd)
        raise ipapi.TryNext()
last_command_hook = LastCommandHook
