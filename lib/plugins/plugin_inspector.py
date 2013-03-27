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
    def enabled_plugins(self):
        class tmp(list):
            def __qmark__(himself):
                report.plugin_inspector('enabled plugins:')
                dat = []
                for p in self: # plugin objs
                    change_types = p.changes.keys()
                    change_types = ' (' + '/'.join(change_types) + ')' \
                                   if change_types else ''
                    report('  plugin: {red}'+ p.filename +'{normal}' + change_types)
                    tmp = p.changes['contribute']
                    contributions = [ args[0] for args,kargs in tmp ] if tmp else []
                    if contributions:
                        contributions = ', '.join(contributions)
                        report('    contributions: '+contributions)
        return tmp(
            self._get_some_plugins('enabled', 1) # plugin names
            )

    def __qmark__(self):
        """ help menu for SmaSh plugins """
        hdr = "{red}SmaSh-plugins{normal}:\n\n"
        _help = [
            "config-file: "+ self.plugins_json_file,
            'to see enabled plugins type: {red}plugins.enabled_plugins?{normal}',
            'to see disabled plugins type: {red}plugins.disabled_plugins?{normal}',
            'to interact with plugin-objects in this runtime, use {red}plugins.plugins{normal}',
            'to enable a disabled plugin type: {red}smash --enable=plugin_name.py{normal}',
            'to disable a enabled plugin type: {red}smash --disable=plugin_name.py{normal}',
            ]
        _help = ''.join([' '*4 + x + '\n' for x in _help])
        report(hdr+_help)
               #

class Plugin(SmashPlugin):
    def install(self):
        from smashlib import ALIASES
        plugins_i = PluginInspector()
        self.contribute('aliases', ALIASES)
        self.contribute('plugins', plugins_i)
        # FIXME: this plugin should really be loaded last
        #       so that this is guaranteed to be accurate.
        for x in dir(smashlib.active_plugins):
            if not x.startswith('__'):
                setattr(plugins_i, x, getattr(smashlib.active_plugins,x))
