# -*- coding: utf-8
""" smashlib.util
"""
import os
import StringIO
import threading

import asciitable

import IPython
from IPython import ColorANSI
from IPython.genutils import Term

opd = os.path.dirname
opj = os.path.join
ope = os.path.exists
tc = ColorANSI.TermColors()

def home(): return os.environ['HOME']

def truncate_fpath(fpath):
    return fpath.replace(home(), '~')

class Prompt(object):
    """ wrapping ipython internals, """
    def _get_template(self):
        """ get the current prompt template """
        opc = getattr(__IPYTHON__.shell, 'outputcache', None)
        if opc:
            return opc.prompt1.p_template
        else:
            return 'error-getting-output-prompt'
    def _set_template(self, t):
        """ set the current prompt template """
        opc = getattr(__IPYTHON__.shell, 'outputcache', None)
        if opc:
            opc.prompt1.p_template = t
    template = property(_get_template, _set_template)
prompt = Prompt()

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
        IPython.ipapi.get().expose_magic(original_magic_name, new_magic)
    chain += [new_func]
    setattr(__IPYTHON__, '_magic_{0}_chain'.format(original_magic_name), chain)

# NOTE: might be obsolete.  this was only needed if/when
#       using the "import all available modules" strategy
CONFLICTING_NAMES  = ('curl gc git time pwd pip pyflakes '
                      'easy_install virtualenv py').split()

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
    return msg.replace('{red}',tc.Red).replace('{normal}',tc.Normal)

def set_complete(func, key):
    ip = IPython.ipapi.get()
    ip.set_hook('complete_command', func, re_key=key)

class Reporter(object):
    """ syntactic sugar for reporting """
    def __init__(self, label=u'>>'):
        self.label = label

    def __getattr__(self, label):
        return Reporter(label)

    def _report(self,msg):
        print colorize('{red}' + self.label + '{normal}: ' + msg)

    def _warn(self,msg):
        return self._report(msg)

    def __call__(self, msg):
        #import smashlib
        return self._report(msg)
    #if smashlib.VERBOSE:

report = Reporter()

def add_shutdown_hook(f):
    __IPYTHON__.hooks['shutdown_hook'].add(f)

def die():
    """
    FIXME: this is horrible, but i remember thinking i had no choice..
    TODO: document reason
    """
    threading.Thread(target=lambda: \
                     os.system('kill -KILL ' + str(os.getpid()))).start()

def list2table(dat, header=[], indent=''):
    """ using asciitable, this function can return
        strings of neatly formated tabular data
    """
    if header: dat=[header] + dat
    s = StringIO.StringIO()
    out = asciitable.write(dat, output=s, Writer=asciitable.FixedWidthNoHeader)
    s.seek(0)
    out = s.read()
    if header:
        out = out.split('\n')
        line1 = out[0]
        out.insert(1,'-'*len(line1))
        out = '\n'.join(out)
    if indent:
        out = out.split('\n')
        out = [indent+line for line in out]
        out = '\n'.join(out)
    return out
