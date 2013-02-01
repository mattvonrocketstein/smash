""" smashlib.main

    NOTE: uses __file__ !
    TODO: install aliases from a file
    TODO: move to hook-based prompt generation if 0.10 supports it
"""
import os, sys
import psutil,os

import demjson

from IPython import ipapi

import smashlib
from smashlib.parser import SmashParser
from smashlib.data import OVERRIDE_OPTIONS
from smashlib.util import clean_namespace, report, die, panic
from smashlib.util import post_hook_for_magic, opj, opd
from smashlib.usage import __doc__ as usage
from smashlib.util import colorize

def reinstall_aliases():
    """ this is here because 'rehash' normally kills
        aliases. this is better than nothing, because
        otherwise you even lose color "ls", but it still
        doesnt quite take into per-project aliases correctly
    """
    from smashlib import ALIASES as aliases
    aliases.install()

VERBOSE   = False
smashlib._meta['SMASH_DIR'] = opd(opd(__file__))
SMASH_ETC_DIR = opj(smashlib._meta['SMASH_DIR'], 'etc')
ip        = ipapi.get()

for option, val in OVERRIDE_OPTIONS.items():
    setattr(ip.options, option, val)

# clean strangeness of the command-line arguments which
# are skewed due to the odd way this script is invoked
sys.argv = sys.argv[1:]

# Plugin installation MUST come before using/instantiating the
# CLI parser, because plugins have the option of modifying it.
smashlib.SMASH_ETC_DIR = SMASH_ETC_DIR
SMASH_EDITOR_CONFIG = opj(SMASH_ETC_DIR, 'editor.json')
smashlib._meta['editor_config'] = SMASH_EDITOR_CONFIG
plugins = smashlib.PluginManager()
plugins.install()

# removes various common namespace collisions between py-modules / shell commands
clean_namespace()

post_hook_for_magic('rehashx', reinstall_aliases)
__IPYTHON__.usage = colorize(usage)
from smashlib.util import report, pre_magic, set_editor
with open(SMASH_EDITOR_CONFIG) as fhandle:
    editor_config = demjson.decode(fhandle.read())
    try:
        editor = editor_config['editor'] \
                 if os.environ.get('DISPLAY', '') else \
                 editor_config['console_editor']
    except KeyError:
        report.bootstrap(("{0} should at least define"
                          " values for 'editor', 'console_editor'").format(
                             SMASH_EDITOR_CONFIG,))

    else:
        report.bootstrap("Your editor is set to: " + set_editor(editor))

    def parameter_s_mutator(parameter_s):

        # as long as it evaluates to something that works as a string,
        # allow for things like "edit dictionary['foo']".  note that this
        # gets weird if you edit a filename="foo" and you type "edit filename",
        # that means you open a file named "filename" instead of one named
        # "foo"
        try: tmp = eval(parameter_s, __IPYTHON__.user_ns)
        except Exception,e: pass
        else:
            if isinstance(tmp, basestring):
                parameter_s = tmp

        # if never_excute_code is set, then "edit foo"
        # will be translated to "edit -x foo"
        if editor_config.get("never_execute_code", False):
            parameter_s = '-x ' + parameter_s
        return parameter_s

    pre_magic('ed', parameter_s_mutator)
    pre_magic('edit', parameter_s_mutator)

try: opts, args = SmashParser().parse_args(sys.argv)
except SystemExit, e: die()
else:
    VERBOSE = VERBOSE or opts.verbose
    import smashlib
    smashlib.VERBOSE = VERBOSE
    #if VERBOSE:
    #report.smash('parsed opts: ' + str(eval(str(opts)).items()))
    if opts.install:
        plugins.cmdline_install_new_plugin(opts.install, opts.enable);
        die()
    elif opts.enable:  plugins.cmdline_enable(opts.enable);   die()
    elif opts.disable: plugins.disable(opts.disable);         die()
    elif opts.list:    plugins.cmdline_list();                die()
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

from smashlib.patches import replace_global_matcher
replace_global_matcher()
