""" SmaSh lib

    Things that will be set in this namespace after bootstrap:

      * smash.PLUGINS :: a list of all installed plugins

"""
from smash.plugins import Plugins
from smash.aliases import Aliases
aliases = Aliases()

import os
opd, opj   = os.path.dirname, os.path.join
config_dir = opj(opd(opd(__file__)), 'etc')
VERBOSE    = True

__all__ = [Plugins, Aliases, aliases, config_dir]
