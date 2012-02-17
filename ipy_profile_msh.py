""" ipython_hacks/ipy_profile_msh

    TODO: replace unix 'which' with a macro that first tries unix-which,
          then, if it fails, tries py.which (from pycmd library)
"""
import os
expanduser = os.path.expanduser

#from ipy_venv_support import activate_venv
from ipy_bonus_yeti import clean_namespace, report
report.msh('importing ipy_profile_msh')

# removes various namespace collisions between
# common py-modules and common unix shell commands
clean_namespace()

## install fabric support
################################################################################
# detects and gives relevant advice when we change
# dirs into a place where a fabric command is present
report.msh('installing fabric support')
from ipy_fabric_support import magic_fabric
magic_fabric.install_into_ipython()

## setup project manager
################################################################################
# consider every directory in ~/code to be a "project"
# by default project.<dir-name> simply changes into that
# directory.  you can add activation hooks for things like
# "start venv if present" or "show fab commands if present"
from medley_ipy import load_medley_customizations
from medley_ipy import load_medley_customizations2
from ipy_project_manager import Project
manager = Project('__main__')

# for my personal projects and their customizations.
# ( robotninja requires hammock's activation first )
manager.bind_all(expanduser('~/code'))
manager.pre_activate('robotninja',
                     lambda: manager.activate(manager.hammock))
manager._ipy_install()

# and here is some extra support for git
################################################################################
from ipy_git_completers import install_git_aliases
install_git_aliases()

## general shell aliases
################################################################################
__IPYTHON__.magic_alias('dhclient sudo dhclient')
__IPYTHON__.magic_alias('dad django-admin.py')
__IPYTHON__.magic_alias('ls ls --color=auto')

import inspect
__IPYTHON__.user_ns.update(getfile=inspect.getfile)

# Medley specific things
manager.bind(expanduser('~/jellydoughnut'))
manager.bind_all(expanduser('~/devel'),
                 post_activate=load_medley_customizations2,
                 post_invoke=load_medley_customizations,)
