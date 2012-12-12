""" plugin_inspector:

      this is a plugin that helps with inspecting the internals
      of smash including aliases, projects, and plugins.

      once this plugin is enabled, type "plugins?" or "aliases?"
      at the prompt for more information.
"""
import asciitable

import smashlib
from smashlib.plugin_manager import PluginManager
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import list2table, colorize


class AliasInspector(object):
    """ """
    @staticmethod
    def _sort_aliases(x,y):
        t1 = cmp(x.affiliation, y.affiliation)
        if t1==0:
            t1 = cmp(x.alias, y.alias)
        return t1

    @property
    def __doc__(self):
        from smashlib import ALIASES as aliases
        lst = [x for x in aliases]
        lst.sort(self._sort_aliases)
        dat=[]
        headers = 'group alias command'.split()
        for alias in aliases:
            nick = alias.alias.split(' ')[0]
            cmd = ' '.join(alias.alias.split(' ')[1:])
            dat.append([alias.affiliation, nick, cmd])
        return colorize("{red}Aliases:{normal}\n\n") + list2table(dat, headers)

class PluginInspector(PluginManager):
    """ """
    def __iter__(self):
        for x in smashlib.PLUGINS:
            yield x

    @property
    def __doc__(self):
        """ lists all plugins """
        dat = [ ]
        fnames = [x.filename for x in smashlib.PLUGINS]
        for p in self.all_plugins:
            dat.append([p,
                        p in self.enabled_plugins,
                        p in fnames])
        dat = sorted(dat,key=lambda x:x[0])
        return ("Smash-plugin information: \n\n"
                "  config-file: {0}\n\n").format(self.plugins_json_file) + \
                list2table(dat, header=['name', 'enabled', 'installed'])

class Plugin(SmashPlugin):
    def install(self):
        self.contribute('plugins', PluginInspector())
        self.contribute('aliases', AliasInspector())
