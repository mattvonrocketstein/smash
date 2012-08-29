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

#from ipy_git_completers import install_git_aliases
from smash.util import clean_namespace, report

VERBOSE      = False
SMASH_DIR    = os.path.dirname(__file__)

ip = ipapi.get()

if VERBOSE: report.smash('importing ipy_profile_msh')

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

## clean and begin main loop.  this first removes various common namespace
## collisions between py-modules and unix shell commands
clean_namespace()

## next clean strangeness of the command-line arguments
## (skewed due to the odd way this script is invoked).
sys.argv = sys.argv[1:]

## do last-minute namespace manipulation and then start parsing on the
## command-line and we're finished bootstrapping.
################################################################################
__IPYTHON__.user_ns.update(getfile=inspect.getfile)

def die():
    import threading
    threading.Thread(target=lambda: os.system('kill -KILL ' + str(os.getpid()))).start()


from smash import Plugins
plugins = Plugins(SMASH_DIR)
plugins.install()

from smash.parser import SmashParser
try: opts,args = SmashParser().parse_args(sys.argv)
except SystemExit, e: die()
else:
    VERBOSE = VERBOSE or opts.verbose
    if VERBOSE:
        report.smash('parsed opts: '+str(eval(str(opts)).items()))
    elif opts.enable:  plugins.enable(opts.enable);   die()
    elif opts.disable: plugins.disable(opts.disable); die()
    elif opts.list:    plugins.list();                 die()
    elif opts.panic:
        print "run this:\n\t","ps aux|grep smash|grep -v grep|awk '{print $2}'|xargs kill -KILL"
        die()
    else:
        for args,kargs,handler in SmashParser.extra_options:
            if getattr(opts, kargs['dest']):
                handler(opts)
