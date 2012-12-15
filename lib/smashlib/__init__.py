""" SmaSh lib

    Things that will be set in this namespace after bootstrap:

      * smashlib.PLUGINS :: a list of all installed plugins

"""
from __future__ import print_function
import os, sys
from types import ModuleType

from cyrusbus import Bus

from smashlib.plugin_manager import PluginManager
from smashlib.aliases import Aliases

ALIASES     = Aliases()
opd, opj    = os.path.dirname, os.path.join
config_dir  = opj(opd(opd(__file__)), 'etc')
VERBOSE     = True
active_plugins = sys.modules['smashlib.active_plugins'] = ModuleType('smashlib.active_plugins')



bus = Bus()
bus.subscribe('post_invoke',
              lambda bus, *args, **kargs: print('post_invoke:' + str(kargs)))
bus.subscribe('pre_invoke',
              lambda bus, *args, **kargs: print('pre_invoke:' + str(kargs)))
bus.subscribe('pre_activate',
              lambda bus, *args, **kargs: print('pre_activate:' + str(kargs)))
bus.subscribe('post_activate',
              lambda bus, *args, **kargs: print('post_activate:' + str(kargs)))

__all__     = [PluginManager, Aliases, aliases, config_dir]
