""" SmaSh lib

    TODO: dox
"""
from smash.plugins import Plugins
from smash.aliases import Aliases
aliases = Aliases()
#plugins = Plugins()
import os
opd,opj = os.path.dirname, os.path.join
config_dir = opj(opd(opd(__file__)), 'config')
__all__ = [Plugins, Aliases, aliases, config_dir]
