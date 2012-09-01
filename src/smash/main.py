""" smash.main

    TODO: install aliases from a file
    TODO: move to hook-based prompt generation if 0.10 supports it
    TODO: replace unix 'which' with a macro that first tries unix-which,
          then, if it fails, tries py.which (from pycmd library)
"""
import os
import sys
import threading

from IPython import ipapi

from smash import Plugins
from smash.parser import SmashParser
from smash.data import OVERRIDE_OPTIONS
from smash.util import clean_namespace, report

VERBOSE      = False
SMASH_DIR    = os.path.dirname(os.path.dirname(__file__))

ip = ipapi.get()

def die():
    """
    FIXME: this is horrible, but i remember thinking i had no choice.. document reason
    """
    threading.Thread(target=lambda: os.system('kill -KILL ' + str(os.getpid()))).start()

for option,val in OVERRIDE_OPTIONS.items():
    setattr(ip.options, option, val)

# removes various common namespace collisions between py-modules / shell commands
clean_namespace()

# clean strangeness of the command-line arguments which
# are skewed due to the odd way this script is invoked
sys.argv = sys.argv[1:]

# Plugin installation MUST come before using/instantiating the
# CLI parser, because plugins have the option of modifying it.
plugins = Plugins(SMASH_DIR)
plugins.install()

try: opts,args = SmashParser().parse_args(sys.argv)
except SystemExit, e: die()
else:
    VERBOSE = VERBOSE or opts.verbose
    if VERBOSE:
        report.smash('parsed opts: '+str(eval(str(opts)).items()))
    elif opts.enable:  plugins.enable(opts.enable);   die()
    elif opts.disable: plugins.disable(opts.disable); die()
    elif opts.list:    plugins.list();                die()
    elif opts.panic:
        print "run this:\n\t","ps aux|grep smash|grep -v grep|awk '{print $2}'|xargs kill -KILL"
        die()
    else:
        # parse any command-line options which are added by plugins
        for args,kargs,handler in SmashParser.extra_options:
            if getattr(opts, kargs['dest']):
                handler(opts)
