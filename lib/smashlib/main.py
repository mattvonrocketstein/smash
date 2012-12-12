""" smashlib.main

    NOTE: uses __file__ !
    TODO: install aliases from a file
    TODO: move to hook-based prompt generation if 0.10 supports it
"""
import os, sys
import psutil,os

from IPython import ipapi

import smashlib
from smashlib.parser import SmashParser
from smashlib.data import OVERRIDE_OPTIONS
from smashlib.util import clean_namespace, report, die
from smashlib.util import post_hook_for_magic

opj = os.path.join
opd = os.path.dirname
VERBOSE   = False
SMASH_DIR = opd(opd(__file__))
SMASH_ETC_DIR = opj(SMASH_DIR, 'etc')
ip        = ipapi.get()

for option, val in OVERRIDE_OPTIONS.items():
    setattr(ip.options, option, val)

# clean strangeness of the command-line arguments which
# are skewed due to the odd way this script is invoked
sys.argv = sys.argv[1:]

# Plugin installation MUST come before using/instantiating the
# CLI parser, because plugins have the option of modifying it.
smashlib.SMASH_ETC_DIR = SMASH_ETC_DIR
smashlib.SMASH_DIR = SMASH_DIR
plugins = smashlib.PluginManager()
plugins.install()
def panic():
    matches = [ x for x in psutil.process_iter() \
                if 'smash' in ' '.join(x.cmdline) ]
    proc = [ x for x in matches if x.pid==os.getpid() ][0]
    matches.remove(proc)
    [ m.kill() for m in matches ]
    proc.kill()

# removes various common namespace collisions between py-modules / shell commands
clean_namespace()
def reinstall_aliases():
    """ this is here because 'rehash' normally kills
        aliases. this is better than nothing, because
        otherwise you even lose color "ls", but it still
        doesnt quite take into per-project aliases correctly
    """
    from smashlib import ALIASES as aliases
    aliases.install()
post_hook_for_magic('rehashx', reinstall_aliases)
from smashlib.usage import __doc__ as usage
__IPYTHON__.usage = usage
import demjson
with open(opj(SMASH_ETC_DIR, 'editor.json')) as fhandle:
    # TODO: test for xwindows so i can actually honor the difference here
    editor_config = demjson.decode(fhandle.read())
    ip.options['editor'] = editor_config['editor']

try: opts, args = SmashParser().parse_args(sys.argv)
except SystemExit, e: die()
else:
    VERBOSE = VERBOSE or opts.verbose
    import smashlib
    smashlib.VERBOSE = VERBOSE
    if VERBOSE:
        report.smash('parsed opts: ' + str(eval(str(opts)).items()))
    elif opts.enable:  plugins.enable(opts.enable);   die()
    elif opts.disable: plugins.disable(opts.disable); die()
    elif opts.list:    plugins.list();                die()
    elif opts.panic:  panic();
    else:
        # parse any command-line options which are added by plugins
        for args,kargs,handler in SmashParser.extra_options:
            if getattr(opts, kargs['dest']):
                handler(opts)


# NOTE: a custom importer will become necessary at some point, if venv-switching
#  support is going to be totally clean.  in practice it is often not a problem,
#  but technically one venv may a different version of a package  than another
#  does, so sys.modules needs to be scrubbed as well as sys.path
"""
import imp
class SmashImporter(object):
    def __init__(self,):
        self.list = []

    def find_module(self, fullname, path=None):
        print '*'*80
        print fullname
        self.path = path
        return None#self
        #if fullname in self.module_names:
        #    self.path = path
        #    return self
        #return None

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]
        module_info = imp.find_module(name, self.path)
        module = imp.load_module(name, *module_info)
        sys.modules[name] = module
        return module
import sys
sys.meta_path = [SmashImporter()]
"""
