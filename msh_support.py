"""
"""
import os
from ipy_venv_support import *

def clean_namespace():
    # clean python namespace in a few places where it shadows unix,
    # or in case it collides with the aliases we'll set up later
    def wipe(name):
        if name in __IPYTHON__.shell.user_ns:
            del __IPYTHON__.shell.user_ns[name]
    names = 'gc git time pwd pip pyflakes easy_install virtualenv'

    [ wipe(x) for x in names.split() ]

def robotninja():
    HOME = os.environ['HOME']
    activate_venv(os.path.join(HOME,'code','hammock','node'))
    __IPYTHON__.ipmagic('cd '+os.path.join(HOME,'code','robotninja'))

class dev(object):
    @property
    def dojo(self):
        robotninja()
dev=dev()
from IPython.macro import Macro
__IPYTHON__.shell.user_ns.update(dev=dev)
