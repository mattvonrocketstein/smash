""" SmaSh lib

    Things that will be set in this namespace after bootstrap:

      * smashlib.PLUGINS :: a list of all installed plugins

"""
import os

from smashlib.plugins import Plugins
from smashlib.aliases import Aliases

ALIASES    = Aliases()
opd, opj   = os.path.dirname, os.path.join
config_dir = opj(opd(opd(__file__)), 'etc')
VERBOSE    = True
__all__    = [Plugins, Aliases, aliases, config_dir]
