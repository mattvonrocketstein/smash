""" plugin_inspector:

    This is a plugin that helps with inspecting the internals
    of smash including aliases, projects, and plugins.

    When this plugin is enabled, type "plugins?" or "aliases?"
    at the prompt for more information.

    TODO: finish 'enabled_plugins' interactive docs, and make
          disabled_plugins work like enabled_plugins does.
"""
import asciitable

import smashlib
from smashlib.plugin_manager import PluginManager
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import list2table, colorize
from smashlib.aliases import Aliases
class PromptInspector(object):
    def __qmark__(self):
        """ help menu for SmaSh prompt """
        hdr = "{red}SmaSh-prompt{normal}:\n\n"
        _help = []
        from smashlib.prompt import prompt
        report(hdr)#+_help)
        for pc in prompt:
            report(pc.name)

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
            """ tmp object so that 'plugins.disabled_plugins?' uses qmark protocol """
            def __qmark__(himself):
                report.plugin_inspector('enabled plugins:')
                dat = []
                for p in self: # plugin objs
                    if p.filename not in himself: continue
                    change_types = p.changes.keys()
                    change_types = ' (' + '/'.join(change_types) + ')' \
                                   if change_types else ''
                    report('  plugin: {red}'+ p.filename +'{normal}' + change_types)
                    tmp = p.changes['contribute']
                    contributions = [ args[0] for args,kargs in tmp ] if tmp else []
                    if contributions:
                        contributions = ', '.join(contributions)
                        report('    contributions: '+contributions)
        return tmp(self._get_some_plugins('enabled', 1))

    @property
    def disabled_plugins(self):
        class tmp(list):
            """ tmp object so that 'plugins.disabled_plugins?' uses qmark protocol """
            def __qmark__(himself):
                report.plugin_inspector('disabled plugins:')
                for p in himself: # plugin objs
                    report('  plugin: {red}'+ p +'{normal}')
        return tmp(self._get_some_plugins('enabled', 0))

    def __qmark__(self):
        """ help menu for SmaSh plugins """
        hdr = "{red}SmaSh-plugins{normal}:\n\n"
        _help = [
            "config-file: "+ self.plugins_json_file,
            'to edit config-file: {red}ed plugins.plugins_json_file{normal}',
            'to see enabled plugins type: {red}plugins.enabled_plugins?{normal}',
            'to see disabled plugins type: {red}plugins.disabled_plugins?{normal}',
            'to interact with plugin-objects in this runtime, use {red}plugins.plugins{normal}',
            'to enable a disabled plugin type: {red}smash --enable=plugin_name.py{normal}',
            'to disable a enabled plugin type: {red}smash --disable=plugin_name.py{normal}',
            ]
        _help = ''.join([' '*4 + x + '\n' for x in _help])
        report(hdr+_help)

class Plugin(SmashPlugin):
    def install(self):
        from smashlib import ALIASES
        plugins_i = PluginInspector()
        prompt_i = PromptInspector()
        self.contribute('aliases', ALIASES)
        self.contribute('plugins', plugins_i)
        self.contribute('prompt', prompt_i)
        # FIXME: this plugin should really be loaded last
        #       so that this is guaranteed to be accurate.
        for x in dir(smashlib.active_plugins):
            if not x.startswith('__'):
                setattr(plugins_i, x, getattr(smashlib.active_plugins,x))
