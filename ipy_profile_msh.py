"""
"""
import os
from ipy_venv_support import *
from ipy_bonus_yeti import clean_namespace
print 'importing ipy_profile_msh'
def robotninja():
    HOME = os.environ['HOME']
    activate_venv(os.path.join(HOME,'code','hammock','node'))
    __IPYTHON__.ipmagic('cd '+os.path.join(HOME,'code','robotninja'))

class dev(object):
    @property
    def dojo(self):
        robotninja()
dev = dev()
from IPython.macro import Macro
__IPYTHON__.shell.user_ns.update(dev=dev)

# remove various collisions between modules/shell commands
import ipy_bonus_yeti
ipy_bonus_yeti.clean_namespace()

from ipy_project_manager import Project
project = Project('__main__')
project.bind_all(os.path.join(os.environ['HOME'], 'code'))
__IPYTHON__.shell.user_ns['proj'] = project
