""" ipython_hacks/ipy_profile_msh

"""
import os

#from ipy_venv_support import activate_venv
from ipy_bonus_yeti import clean_namespace

from IPython import ColorANSI
from IPython.genutils import Term
tc = ColorANSI.TermColors()
def colorize(msg):
    """ """
    return msg.format(red=tc.Red,normal=tc.Normal)
print colorize('{red}msh{normal}: importing ipy_profile_msh')

# removes various namespace collisions between
# common py-modules and common unix shell commands
import ipy_bonus_yeti
ipy_bonus_yeti.clean_namespace()

# consider every directory in ~/code to be a "project"
# by default project.<dir-name> simply changes into that
# directory.  you can add activation hooks for things like
# "start venv if present" or "show fab commands if present"
from ipy_project_manager import Project
manager = Project('__main__')
manager.bind_all(os.path.expanduser('~/code'))

# robotninja requires hammock's activation first, so register that
manager.pre_activate('robotninja',
                     lambda: manager.activate(manager.hammock))
manager.ipy_install()
