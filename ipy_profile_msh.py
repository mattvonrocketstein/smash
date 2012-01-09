""" ipython_hacks/ipy_profile_msh

"""
import os
from IPython.macro import Macro

from ipy_venv_support import activate_venv
from ipy_bonus_yeti import clean_namespace

print 'importing ipy_profile_msh'
HOME = os.environ['HOME']

# removes various namespace collisions between
# common py-modules and common unix shell commands
import ipy_bonus_yeti
ipy_bonus_yeti.clean_namespace()

# consider every directory in ~/code to be a "project"
# by default project.<dir-name> simply changes into that
# directory.  you can add activation hooks for things like
# "start venv if present" or "show fab commands if present"
from ipy_project_manager import Project
project_manager = Project('__main__')
project_manager.bind_all(os.path.join(os.environ['HOME'], 'code'))
project_manager.pre_activate('robotninja',
                             lambda: project_manager.activate(project_manager.hammock))
project_manager.ipy_install()

# project.robotninja.pre_activate_hook(lambda: project.activate(project.hammock))
