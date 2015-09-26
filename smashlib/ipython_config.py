#
# SmaSh system configuration file
#
# Do not edit this file.
# The file in ~/.smash is reset from smashlib source on every run,
# and thus cannot be edited. To override these values, edit instead
# the user configuration file: ~/.smash/config.py (or inside smash
# type "ed_ed").
#
from smashlib.editor import get_editor
from smashlib._logging import smash_log
msg = '..loading system config: ' + __file__
smash_log.debug(msg)

_ = get_config()  # NOQA

# set editor from $EDITOR if possible
_.TerminalInteractiveShell.editor = get_editor()

_.Smash.load_bash_aliases = True
_.Smash.load_bash_functions = True

# load toplevel extensions
##########################################################################
_.InteractiveShellApp.extensions.append("smashlib.ipy_smash")

# every smash component gets it's own verbosity setting.
# this mostly controls the printing of debugging info
##########################################################################
_.Smash.verbose = True
_.DoWhatIMean.verbose = False
_.DjangoPlugin.verbose = True
_.Summarize.verbose = False
_.ProjectManager.verbose = False
_.ChangeDirHooks.verbose = False
_.VirtualEnvSupport.verbose = False

# cross-cutting verbosity configs
##########################################################################
_.Smash.ignore_warnings = True
_.Smash.verbose_events = False

# include various things that used to be
# done in profile_pysh/ipython_config.py
##########################################################################
_.InteractiveShell.separate_in = ''
_.InteractiveShell.separate_out = ''
_.InteractiveShell.separate_out2 = ''
#_.InteractiveShellApp.extensions = ['autoreload']
#_.InteractiveShellApp.exec_lines = ['%autoreload 2']
#.InteractiveShellApp.exec_lines.append('print("Warning: disable autoreload in ipython_config.py to improve performance.")')

_.TerminalIPythonApp.display_banner = False
_.TerminalInteractiveShell.confirm_exit = False

# If False, only the completion results from
# the first non-empty completer will be returned.
##########################################################################
_.IPCompleter.merge_completions = True


# load optional smash extensions
# _.InteractiveShellApp.extensions.append('powerline.bindings.ipython.post_0_11')
_.Smash.plugins.append('smashlib.plugins.prompt')
_.Smash.plugins.append('smashlib.plugins.history_completer')
_.Smash.plugins.append('smashlib.plugins.smash_completer')

# handlers for "smash -c" and "smash --update", respectively
_.Smash.plugins.append('smashlib.plugins.cli_command_runner')
_.Smash.plugins.append('smashlib.plugins.cli_update')

# automatically shows timer info for commands taking longer than 5s
_.Smash.plugins.append('smashlib.plugins.time_long_commands')

_.Smash.plugins.append('smashlib.plugins.post_input')
_.Smash.plugins.append('smashlib.plugins.uninstall_plugin')
_.Smash.plugins.append('smashlib.plugins.prefilter_dot')
_.Smash.plugins.append('smashlib.plugins.prompt')

# enhanced which:
#   provides information about binaries on $PATH
#   provides information about python libraries (in the current venv, if any)
_.Smash.plugins.append('smashlib.plugins.which')

#experimental
_.Smash.plugins.append('smashlib.plugins._django')

_.Smash.plugins.append('smashlib.plugins.prefilter_url')

## these are plugins and therefore technically
## optional, but fairly critical for smash core

_.Smash.plugins.append('smashlib.plugins.venv')
_.Smash.plugins.append('smashlib.plugins.cd_hooks')
_.Smash.plugins.append('smashlib.plugins.project_manager')
_.Smash.plugins.append('smashlib.plugins.handle_cmd_failure')

## these plugins are more optional and idiosyncratic, but well tested
_.Smash.plugins.append("smashlib.plugins.dwim")
_.Smash.plugins.append("smashlib.plugins._fabric")
_.Smash.plugins.append("smashlib.plugins.autojump")
_.Smash.plugins.append('smashlib.plugins.summarize')
_.Smash.plugins.append('smashlib.plugins.cmd_env')


## more experimental
_.Smash.plugins.append("smashlib.plugins.python_comp_tools")

# setup default configuration for the linter (used by "project manager" plugin)
##########################################################################
_.PyLinter.verbose = True
_.PyLinter.ignore_pep8 = True
_.PyLinter.ignore_undefined_names = [
    'get_ipython',
    ['get_config', '.*_config.py'],
    ['load_subconfig', '.*ipython_config.py'],
]

# configure the prompt extension with some reasonable defaults.
##########################################################################
_.PromptManager.justify = False

# configure the project manager extension
##########################################################################
projects = _.ProjectManager

# this is safe even when the directories do not exist
projects.search_dirs.append('~/code')
projects.search_dirs.append('~/projects')

# load user's project manager configs from the ~/.smash/etc json
# see docs at: http://mattvonrocketstein.github.io/smash/project_manager.html
from smashlib.config import SmashConfig
config = SmashConfig(_)
config.append_from_etc(projects.search_dirs, 'search_dirs.json')
config.update_from_etc(projects.project_map, 'projects.json')
config.update_from_etc(projects.macro_map, 'macros.json')
config.update_from_etc(projects.alias_map, 'aliases.json')
config.append_from_etc(_.Smash.plugins, 'plugins.json')
config.update_from_etc(projects.env_map, 'env.json')

# configure the ipython app
##########################################################################
app = _.InteractiveShellApp

# NB: Here's an easy way to issue adhoc
# commands, or modify the user namespace:
#
# app.exec_lines.append("print 'hello world!'")
# app.exec_lines.append("side_effect='whatever'")


# load smash user config.  NB: this must happen last!
##########################################################################
from smashlib.config import SmashUserConfig
SmashUserConfig.load(globals())
