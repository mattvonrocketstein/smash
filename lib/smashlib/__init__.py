""" SmaSh lib

    Things that will be set in this namespace after bootstrap:

      * smashlib.PLUGINS :: a list of all installed plugins

"""
import os

from smashlib.plugin_manager import PluginManager
from smashlib.aliases import Aliases

ALIASES    = Aliases()
opd, opj   = os.path.dirname, os.path.join
config_dir = opj(opd(opd(__file__)), 'etc')
VERBOSE    = True
__all__    = [PluginManager, Aliases, aliases, config_dir]
