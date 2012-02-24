""" smash/ipy_profile_msh

    TODO: install aliases from a file
    TODO: move to hook-based prompt generation if 0.10 supports it
    TODO: replace unix 'which' with a macro that first tries unix-which,
          then, if it fails, tries py.which (from pycmd library)
"""
import os
import sys
import inspect

from IPython import ipapi

from ipy_fabric_support import magic_fabric
from ipy_git_completers import install_git_aliases
from ipy_bonus_yeti import clean_namespace, report

ip = ipapi.get()
expanduser = os.path.expanduser

report.msh('importing ipy_profile_msh')

## install fabric support. detects and gives relevant advice if we change into
## a directory where a fabric command is present.  also provides tab-completion
################################################################################
report.msh('installing fabric support')
magic_fabric.install_into_ipython()

# git VCS: this installs git aliases.  TODO: where did i install the completers?
################################################################################
install_git_aliases()

## install various overrides into ip.options. doing it here puts as much code as
## possible actually in pure python instead of in ipython's weird rc format file
################################################################################
OVERRIDE_OPTIONS = dict(
    confirm_exit = 0,
    prompt_in1= ' \C_Red${__IPYTHON__._cgb()} \C_LightBlue[\C_LightCyan\Y3\C_LightBlue]>',
    include = list(set(ip.options.include + ['ipythonrc-pysh',
                                             'ipythonrc-git-aliases',
                                             'ipythonrc-bash-aliases', ])),

    # 'complete' only completes as much as possible while
    # 'menu-complete'  cycles through all possible completions.
    # readline_parse_and_bind tab: menu-complete
    readline_parse_and_bind = list(set(ip.options.readline_parse_and_bind + \
                              ['tab: complete',
                               '"\C-l": clear-screen',      # control+L
                               '"\b": backward-kill-word',  # control+delete
                               ])),

    # readline_omit__names 1: omit showing any names starting with two __
    # readline_omit__names 2: completion will omit all names beginning with _
    # Regardless, typing a _ after the period and hitting <tab>: 'name._<tab>'
    # will always complete attribute names starting with '_'.
    readline_omit__names = 1,

    # uses emacs daemon to open files for objects. as if by magic
    # try it out.. "%edit SomeModelClass" opens the file!
    editor = 'emacsclient')
for option,val in OVERRIDE_OPTIONS.items():
    setattr(ip.options, option, val)

report.msh('setting prompt')
__IPYTHON__._cgb = lambda : os.popen("current_git_branch").read().strip()

## general shell aliases.  this stuff is somewhat idiosyncratic, but it seems
## like if it's not relevant it simply won't be used.  no harm no foul.
################################################################################
__IPYTHON__.magic_alias('dhclient sudo dhclient')
__IPYTHON__.magic_alias('dad django-admin.py')
__IPYTHON__.magic_alias('ls ls --color=auto')
__IPYTHON__.magic_alias('apt-get sudo apt-get')


## clean and begin main loop.  this first removes various common namespace
## collisions between py-modules and unix shell commands. then we clean up the
## strangeness of the command-line arguments (which are skewed due to the odd
## way this script is invoked).  after it's clean, we can do last-minute
## namespace manipulation and then start parsing on the
## command-line and we're finished bootstrapping.
################################################################################
clean_namespace()
sys.argv = sys.argv[1:]
__IPYTHON__.user_ns.update(getfile=inspect.getfile)

## setup project manager
################################################################################
from ipy_project_manager import Project
__manager__ = Project('__main__')
__manager__._ipy_install()

## idiosyncratic stuff.  TODO: this part should not be in this file!
################################################################################
# consider every directory in ~/code to be a "project"
# by default project.<dir-name> simply changes into that
# directory.  you can add activation hooks for things like
# "start venv if present" or "show fab commands if present"
from medley_ipy import load_medley_customizations
from medley_ipy import load_medley_customizations2

# for my personal projects and their customizations.
# ( robotninja requires hammock's activation first )
__manager__.bind_all(expanduser('~/code'))
__manager__.pre_activate('robotninja',
                         lambda: manager.activate(manager.hammock))

# Medley specific things
__manager__.bind(expanduser('~/jellydoughnut'))
__manager__.bind_all(expanduser('~/devel'),
                     post_activate=load_medley_customizations2,
                     post_invoke=load_medley_customizations,)
