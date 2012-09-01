""" smash.util
"""

import os

import IPython
from IPython import ColorANSI
from IPython.genutils import Term

tc = ColorANSI.TermColors()

CONFLICTING_NAMES  = 'curl gc git time pwd pip pyflakes easy_install virtualenv py'.split()
CONFLICTING_NAMES += ['smash']

def post_hook_for_magic(original_magic_name, new_func):
    """ attaches a new post-run hook for an existing magic function """
    old_magic = getattr(__IPYTHON__, 'magic_' + original_magic_name)
    def new_magic(self, parameter_s=''):
        out = old_magic(parameter_s=parameter_s)
        new_func()
        return out
    new_magic._wrapped = old_magic
    IPython.ipapi.get().expose_magic(original_magic_name, new_magic)

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

class Reporter(object):
    """ syntactic sugar for reporting """
    def __init__(self, label=''):
        self.label = label

    def __getattr__(self, label):
        return Reporter(label)

    def __call__(self, msg):
        print colorize('{red}' + self.label + '{normal}: ' + msg)
report = Reporter()