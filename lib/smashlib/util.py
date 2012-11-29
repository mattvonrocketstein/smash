""" smashlib.util
"""
import os
import asciitable

import IPython
from IPython import ColorANSI
from IPython.genutils import Term

tc = ColorANSI.TermColors()

def get_prompt_t():
    """ get the current prompt template """
    return __IPYTHON__.shell.outputcache.prompt1.p_template

def set_prompt_t(t):
    """ set the current prompt template """
    __IPYTHON__.shell.outputcache.prompt1.p_template = t

def post_hook_for_magic(original_magic_name, new_func):
    """ attach a new post-run hook for an existing magic function """
    old_magic = getattr(__IPYTHON__, 'magic_' + original_magic_name)
    def new_magic(self, parameter_s=''):
        out = old_magic(parameter_s=parameter_s)
        new_func()
        return out
    new_magic._wrapped = old_magic
    IPython.ipapi.get().expose_magic(original_magic_name, new_magic)

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
    return msg.format(red=tc.Red, normal=tc.Normal)

def set_complete(func, key):
    ip = IPython.ipapi.get()
    ip.set_hook('complete_command', func, re_key=key)

class Reporter(object):
    """ syntactic sugar for reporting """
    def __init__(self, label=''):
        self.label = label

    def __getattr__(self, label):
        return Reporter(label)
    def _report(self,msg):
        print colorize('{red}' + self.label + '{normal}: ' + msg)
    def _warn(self,msg):
        return self._report(msg)

    def __call__(self, msg):
        import smashlib
        if smashlib.VERBOSE:
            return self._report(msg)
report = Reporter()

import threading
def die():
    """
    FIXME: this is horrible, but i remember thinking i had no choice..
    TODO: document reason
    """
    threading.Thread(target=lambda: \
                     os.system('kill -KILL ' + str(os.getpid()))).start()

import StringIO
def list2table(dat, header=[]):
    if header: dat=[header] + dat
    s = StringIO.StringIO()
    out = asciitable.write(dat, output=s, Writer=asciitable.FixedWidthNoHeader)
    s.seek(0)
    out = s.read()
    if header:
        out = out.split('\n')
        line1 = out[0]
        out.insert(1,'-'*len(line1))
        return '\n'.join(out)
    return out
