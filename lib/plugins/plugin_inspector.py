""" plugin_inspector:

    This is a plugin that helps with inspecting the internals
    of smash including aliases, projects, and plugins.

    When this plugin is enabled, type "plugins?" or "aliases?"
    at the prompt for more information.
"""
import asciitable

import smashlib
from smashlib.plugin_manager import PluginManager
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import list2table, colorize
from smashlib.aliases import Aliases

class PluginInspector(PluginManager):
    """ """
    def __iter__(self):
        for x in smashlib.PLUGINS:
            yield x

    @property
    def plugins(self):
        return smashlib.PLUGINS

    @property
    def __doc__(self):
        """ lists all plugins """
        dat = [ ]
        fnames = [x.filename for x in smashlib.PLUGINS]
        for p in self.all_plugins:
            dat.append([p,
                        p in self.enabled_plugins,
                        str(0)])
        dat = sorted(dat,key=lambda x:x[0])
        return ("Smash-plugin information:\n"
                "  config-file: {0}\n").format(self.plugins_json_file) + \
                '  for subsets of this info, type:\n' + \
                '    plugins.enabled._plugins?\n' + \
                '    plugins.disabled_plugins?\n\n'+\
                list2table(dat, header=['name', 'enabled', 'errors'])

class Plugin(SmashPlugin):
    def install(self):
        from smashlib import ALIASES
        plugins_i = PluginInspector()
        self.contribute('aliases', ALIASES)
        self.contribute('plugins', plugins_i)
        # TODO: this plugin should really be loaded last
        #       so that this is guaranteed to be accurate.
        for x in dir(smashlib.active_plugins):
            if not x.startswith('__'):
                setattr(plugins_i, x, getattr(smashlib.active_plugins,x))
