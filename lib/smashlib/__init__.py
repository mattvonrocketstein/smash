""" SmaShlib

    Things that will be set in this namespace after bootstrap:

      * smashlib.PLUGINS
         a list of all installed plugins

      * smashlib._meta
         a dictionary with the smash installation dir,
         paths to various configuration files, etc.
"""
from __future__ import print_function
import os, sys
from types import ModuleType

from cyrusbus import Bus

from smashlib.plugin_manager import PluginManager
from smashlib.aliases import Aliases

VERBOSE     = True
ALIASES     = Aliases()
opd, opj    = os.path.dirname, os.path.join
active_plugins = sys.modules['smashlib.active_plugins'] = ModuleType('smashlib.active_plugins')

_meta = dict( config_dir = opj(opd(opd(__file__)), 'etc'),
              bin_dir = opj(opd(opd(__file__)), 'bin'),)
_meta.update(smash_rc=opj(_meta['config_dir'], 'smash.rc'))

def fac(m):
    from smashlib.util import report_if_verbose
    return lambda bus, *args, **kargs: getattr(report_if_verbose, m)(str(kargs) )


bus = Bus()
bus.subscribe('post_invoke',   fac('post_invoke'))
bus.subscribe('pre_invoke',    fac('pre_invoke'))
bus.subscribe('pre_activate',  fac('pre_activate'))
bus.subscribe('post_activate', fac('post_activate'))
bus.subscribe('pre_deactivate',  fac('pre_deactivate'))
bus.subscribe('post_deactivate', fac('post_deactivate'))
