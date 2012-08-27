""" smash/ipy_profile_msh

    TODO: install aliases from a file
    TODO: move to hook-based prompt generation if 0.10 supports it
    TODO: replace unix 'which' with a macro that first tries unix-which,
          then, if it fails, tries py.which (from pycmd library)
"""
import os
import sys
import inspect
from optparse import OptionParser

import demjson
from IPython import ipapi

from ipy_fabric_support import magic_fabric
from ipy_git_completers import install_git_aliases
from ipy_bonus_yeti import clean_namespace, report

SMASH_DIR         = os.path.dirname(__file__)

ip = ipapi.get()

report.smash('importing ipy_profile_msh')

## install fabric support. detects and gives relevant advice if we change into
## a directory where a fabric command is present.  also provides tab-completion
################################################################################
report.smash('installing fabric support')
magic_fabric.install_into_ipython()

# git VCS: this installs git aliases.  TODO: where did i install the completers?
################################################################################
install_git_aliases()

## install various overrides into ip.options. doing it here puts as much code as
## possible actually in pure python instead of in ipython's weird rc format file
################################################################################
OVERRIDE_OPTIONS = dict(
    autoedit_syntax=1,
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

report.smash('setting prompt to use git vcs')
__IPYTHON__._cgb = lambda : os.popen("current_git_branch").read().strip()

from ipy_smash_aliases import install_aliases
install_aliases()

import ipy_ytdl

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
__manager__.bind_all('~/code')
#__manager__.pre_activate('robotninja',
#                         lambda: __manager__.activate(manager.hammock))

# Medley specific things
__manager__.bind('~/jellydoughnut')
__manager__.bind_all('~/devel',
                     post_activate=load_medley_customizations2,
                     post_invoke=load_medley_customizations,)

def get_parser():
    parser = OptionParser()
    parser.add_option("--panic", dest="panic",
                      default=False, action="store_true",
                      help="kill all running instances of 'smash'", )
    parser.add_option('-p', "--project",
                      dest="project", default='',
                      help="specify a project to initialize", )
    parser.add_option('-i', '--install',
                      dest='install', default='',
                      help='install new smash module')
    parser.add_option('-l', '--list',
                      action='store_true',dest='list', default=False,
                      help='list available plugins and their status')
    parser.add_option('--enable',
                      dest='enable', default='',
                      help='enable plugin by name')
    parser.add_option('--disable',
                      dest='disable', default='',
                      help='disable plugin by name')
    return parser

def die():
    import threading
    threading.Thread(target=lambda: os.system('kill -KILL ' + str(os.getpid()))).start()


class Plugins(object):
    plugins_json_file = os.path.join(SMASH_DIR, 'plugins.json')
    report = staticmethod(report.plugins)

    def disable(self, name):
        self.report('disabling {0}'.format(name))

    def enable(self, name):
        self.report('enabling {0}'.format(name))

    @property
    def plugin_data(self):
        return demjson.decode(open(self.plugins_json_file, 'r').read())

    def list(self):
        # reconstructed because `plugins_json_file` may not be up to date with system
        plugin_data = self.plugin_data
        py_files          = [ fname for fname in os.listdir(SMASH_DIR) if fname.endswith('.py') ]
        plugins  = dict([[fname, plugin_data.get(fname, 0)] for fname in py_files])
        enabled  = [ fname for fname in plugins if plugins[fname] == 1 ]
        disabled = [ fname for fname in plugins if plugins[fname] == 0 ]
        if enabled:
            self.report('enabled plugins')
            for p in enabled: print '  ',p
            print ; print
        if disabled:
            self.report('disabled plugins:')
            for p in disabled: print '  ',p


plugins = Plugins()
try: opts,args = get_parser().parse_args(sys.argv)
except SystemExit, e: die()
else:
    report.smash('parsed opts: '+str(eval(str(opts)).items()))
    if opts.project:
        report.cli('parsing project option')
        getattr(__manager__, opts.project).activate
    elif opts.enable:  plugins.enable(opts.enable);   die()
    elif opts.disable: plugins.disable(opts.disable); die()
    elif opts.list:    plugins.list();                 die()
    elif opts.panic:
        print "run this:\n\t","ps aux|grep smash|grep -v grep|awk '{print $2}'|xargs kill -KILL"
        die()

shh = __IPYTHON__.hooks['shutdown_hook']
gop = __IPYTHON__.hooks['pre_prompt_hook']
gop.add(__manager__.check)
shh.add(lambda: __manager__.shutdown())

# patch reset to clean up the display a la bash, not reset the namespace.
from IPython.Magic import Magic
def reset(himself,parameter_s=''):
    __IPYTHON__.system('reset')
    return 'overridden'
Magic.magic_reset = reset
