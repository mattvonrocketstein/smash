# -*- coding: utf-8
#
# DEFAULT USER-CONFIGURATION FILE FOR SMASH.
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

_ = get_config()
get_config = eval('get_config') # shut up the linter

# always inherit the default ipython profile's configuration
#load_subconfig('ipython_config.py', profile='default')

from smashlib.config import SmashConfig
config = SmashConfig(_)

# every smash component gets it's own verbosity setting.
# this mostly controls the printing of debugging info
_.Smash.ignore_warnings = True
_.Smash.verbose = False
_.Smash.verbose_events = True
_.LiquidPrompt.verbose = False
_.ProjectManager.verbose = False
_.ChangeDirHooks.verbose = False
_.VirtualEnvSupport.verbose = True

_.PyLinter.verbose=True
_.PyLinter.ignore_pep8 = True

# begin Change-Dir-hooks configuration: add any custom hooks here
#
#_.ChangeDirHooks.change_dir_hooks.append(
#    "smashlib.ipy_cd_hooks.ChangeDirHooks.test_change_message")


# begin project manager configuration.
#
# the project manager can be configured either from this file directly,
# or from ~/.smash/etc, based on json there.  in each case you can consult
# the corresponding json schema for more information
#
projects = _.ProjectManager
projects.search_dirs.append(config.load_from_etc('search_dirs.json'))
projects.project_map.update(config.load_from_etc('projects.json'))
projects.alias_map.update(config.load_from_etc('aliases.json'))
projects.macro_map.update(config.load_from_etc('macros.json'))
projects.venv_map.update(config.load_from_etc('venvs.json'))
