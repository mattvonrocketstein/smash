# -*- coding: utf-8
# User-configuration file for SmaSh.
#
# For examples of stuff you might like to do in here, check out:
#
#  1) default ipython config: ~/.ipython/profile_default/ipython_config.py
#  2) default smash config: ~/.smash/profile_SmaSh/ipython_config.py
#
# Note that while the main configuration file at ~/.smash/profile_SmaSh
# cannot be edited, you can make any overrides you would like to make there
# in here instead.
#

c = get_config()

# every smash component gets it's own verbosity setting.
# this mostly controls the printing of debugging info
c.Smash.ignore_warnings = True
c.Smash.verbose = False
c.Smash.verbose_events = True
c.LiquidPrompt.verbose = False
c.ProjectManager.verbose = False
c.ChangeDirHooks.verbose = False
c.VirtualEnvSupport.verbose = True

c.PyLinter.verbose=True
c.PyLinter.ignore_pep8 = True
c.PyLinter.ignore_undefined_names='get_ipython'.split()

# add custom directory hooks here
#c.ChangeDirHooks.change_dir_hooks.append(
#    "smashlib.ipy_cd_hooks.ChangeDirHooks.test_change_message")

# everything below this line should not ultimately be in this file..
#
c.TerminalInteractiveShell.editor = 'emacsclient -n'

# project manager configuration
projects = c.ProjectManager
projects.search_dirs.append('~/code')
projects.project_map.update(dict(toybox='/vagrant'))
projects.venv_map.update(dict(robotninja='~/code/hammock/'))
projects.venv_map.update(dict(emax='~/.emax'))
projects.venv_map.update(dict(toybox='/vagrant/guest_venv'))

# TODO: SmashAliasManager, which respects project settings
projects.alias_map.update(dict(
    __smash__ = [
        ('ack', 'ack-grep'),
        ('st', 'git status'),
        ('gds', 'git diff --stat'),
        ('gd', 'git diff'),
        ('irc','xchat -d ~/code/dotfiles/xchat_default&'),
        ],

    ))
