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

# add custom directory hooks here
c.ChangeDirHooks.change_dir_hooks.append(
    "smashlib.ipy_cd_hooks.ChangeDirHooks.test_change_message")

c.Smash.ignore_warnings = True

# every smash component gets it's own verbosity setting.
# this mostly controls the printing of debugging info
c.Smash.verbose = False
c.Smash.verbose_events = False
c.LiquidPrompt.verbose = False
c.ProjectManager.verbose = False
c.ChangeDirHooks.verbose = False
c.VirtualEnvSupport.verbose = False
c.PyLinter.verbose = True
c.PyLinter.ignore_pep8 = True


# everything below this line should not ultimately be in this file..
#
c.TerminalInteractiveShell.editor = 'emacsclient -n'

# TODO: SmashAliasManager, which respects project settings
c.AliasManager.user_aliases.append(('ack', 'ack-grep'))
c.AliasManager.user_aliases.append(('st', 'git status'))
c.AliasManager.user_aliases.append(('gds', 'git diff --stat'))
c.AliasManager.user_aliases.append(('gd', 'git diff'))
c.AliasManager.user_aliases.append(
    ('irc','xchat -d ~/code/dotfiles/xchat_default&'))
