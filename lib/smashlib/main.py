""" smashlib.main

    NOTE: uses __file__ !
    TODO: install aliases from a file
    TODO: move to hook-based prompt generation if 0.10 supports it
"""
import os
import sys


from IPython import ipapi

import smashlib
from smashlib.parser import SmashParser
from smashlib.data import OVERRIDE_OPTIONS
from smashlib.util import clean_namespace, report, die

VERBOSE   = False
SMASH_DIR = os.path.dirname(os.path.dirname(__file__))
ip        = ipapi.get()

for option,val in OVERRIDE_OPTIONS.items():
    setattr(ip.options, option, val)

# clean strangeness of the command-line arguments which
# are skewed due to the odd way this script is invoked
sys.argv = sys.argv[1:]

# Plugin installation MUST come before using/instantiating the
# CLI parser, because plugins have the option of modifying it.
smashlib.SMASH_DIR = SMASH_DIR
plugins = smashlib.Plugins()
plugins.install()

try: opts, args = SmashParser().parse_args(sys.argv)
except SystemExit, e: die()
else:
    VERBOSE = VERBOSE or opts.verbose
    import smashlib
    smashlib.VERBOSE = VERBOSE
    if VERBOSE:
        report.smash('parsed opts: '+str(eval(str(opts)).items()))
    elif opts.enable:  plugins.enable(opts.enable);   die()
    elif opts.disable: plugins.disable(opts.disable); die()
    elif opts.list:    plugins.list();                die()
    elif opts.panic:
        #FIXME: do this for them instead of telling them how
        report.smash("run this:\n\t",
                     ("ps aux|grep smash|grep -v grep|"
                      "awk '{print $2}'|xargs kill -KILL"))
        die()
    else:
        # parse any command-line options which are added by plugins
        for args,kargs,handler in SmashParser.extra_options:
            if getattr(opts, kargs['dest']):
                handler(opts)

# removes various common namespace collisions between py-modules / shell commands
clean_namespace()

def reinstall_aliases():
    """ this is here because 'rehash' normally kills
        aliases. this is better than nothing, because
        otherwise you even lose color "ls", but it still
        doesnt quite take into per-project aliases correctly
    """
    from smashlib import aliases
    aliases.install()
from smashlib.util import post_hook_for_magic
post_hook_for_magic('rehashx', reinstall_aliases)

from smashlib.usage import __doc__ as usage
__IPYTHON__.usage = usage
