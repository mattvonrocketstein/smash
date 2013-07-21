""" SmaShlib

    Things that will be set in this namespace after bootstrap:

      * smashlib.PLUGINS
         a list of all installed plugins
      * smashlib.ALIASES
         a list of aliases and their project affiliations
      * smashlib._meta
         a dictionary with the smash installation dir,
         paths to various configuration files, etc.
"""

from __future__ import print_function
import sys, types


from smashlib.bus import bus
from smashlib.plugin_manager import PluginManager
from smashlib.aliases import Aliases
from smashlib.python import opd, opj, ope, mkdir

VERBOSE = True
ALIASES = Aliases()

active_plugins = sys.modules['smashlib.active_plugins'] = \
                 types.ModuleType('smashlib.active_plugins')

_meta = dict( config_dir = opj(opd(opd(__file__)), 'etc'),
              bin_dir    = opj(opd(opd(__file__)), 'bin'),
              tmp_dir    = opj(opd(opd(__file__)), 'tmp'), )
_meta.update(smash_rc=opj(_meta['config_dir'], 'smash.rc'))
if not ope(_meta['tmp_dir']): mkdir(_meta['tmp_dir'])
