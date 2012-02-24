""" smash/ipy_profile_msh

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
from IPython import ipapi
ip = ipapi.get()
# 'complete' only completes as much as possible while
# 'menu-complete'  cycles through all possible completions.
# readline_parse_and_bind tab: menu-complete
report.msh('setting parsebind rules')
ip.options.readline_parse_and_bind += [
    'tab: complete',
    '"\C-l": clear-screen', #      # control+L
    '"\b": backward-kill-word',  # control+delete
    ]
ip.options.readline_parse_and_bind = list(set(ip.options.readline_parse_and_bind))
ip.options.confirm_exit = 0

report.msh('setting prompt')
__IPYTHON__._cgb = lambda : os.popen("current_git_branch").read().strip()
#ip.options.prompt_in1= ' \C_Red${os.popen("current_git_branch").read().strip()} \C_LightBlue[\C_LightCyan\Y3\C_LightBlue]>'
ip.options.prompt_in1= ' \C_Red${__IPYTHON__._cgb()} \C_LightBlue[\C_LightCyan\Y3\C_LightBlue]>'

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


# TODO: move prompt generation here if 0.10 supports it
#ip.set_hook("generate_prompt", myhdl_inputprompt)
#ip.set_hook("generate_output_prompt", myhdl_outputprompt)


# readline_omit__names 1: omit showing any names starting with two __
# readline_omit__names 2: completion will omit all names beginning with _
# Regardless, typing a _ after the period and hitting <tab>: 'name._<tab>'
# will always complete attribute names starting with '_'.
ip.options.readline_omit__names = 1

# uses emacs daemon to open files for objects as if by magic
# try it out.. "%edit SomeModelClass" opens the file!
ip.options.editor = 'emacsclient'

ip.options.include = list(set(ip.options.include + [
    'ipythonrc-pysh',
    'ipythonrc-git-aliases',
    'ipythonrc-bash-aliases', ]))

class SmashPrompt(object):
    def update_prompt(self, ishell):
        print 'testing', self,ishell
        ip.options.prompt_in1 = 'testing' #
smash_prompt = SmashPrompt()
#ip.set_hook("pre_prompt_hook", smash_prompt.update_prompt)

import sys; sys.argv=sys.argv[1:]
