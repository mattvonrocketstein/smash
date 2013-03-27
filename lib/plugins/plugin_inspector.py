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

    #@property
    #def disabled_plugins
    # this doesnt work as advertised with 'plugins.disabled_plugins?'
    # can properties call super?

    @property
    def plugins(self):
        return smashlib.PLUGINS

    def __qmark__(self):
        """ lists all plugins """
        dat = [ ]
        fnames = [x.filename for x in smashlib.PLUGINS]
        for p in self.all_plugins:
            dat.append([p,
                        p in self.enabled_plugins,
                        str(0)])
        dat = sorted(dat,key=lambda x:x[0])
        hdr = "{red}SmaSh-plugins{normal}:\n\n"
        _help = [
            "config-file: "+ self.plugins_json_file,
            'to see enabled plugins type: {red}plugins.enabled._plugins?{normal}',
            'to see disabled plugins type: {red}plugins.disabled_plugins?{normal}',
            'to interact with plugin-objects in this runtime, use {red}plugins.plugins{normal}',
            'to enable a disabled plugin type: {red}smash --enable=plugin_name.py{normal}',
            'to disable a enabled plugin type: {red}smash --disable=plugin_name.py{normal}',
            ]
        _help = ''.join([' '*4 + x + '\n' for x in _help])
        report(hdr+_help)
               #list2table(dat, header=['name', 'enabled', 'errors']))

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
