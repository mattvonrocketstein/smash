""" plugin that provides a plugin inspector
"""
import asciitable

import smash
from smash.plugins import Plugins, SmashPlugin
from smash.util import list2table

class PluginInspector(Plugins):
    @property
    def __doc__(self):
        """ lists all plugins """
        dat = [ ]
        fnames = [x.filename for x in smash.PLUGINS]
        for p in self.all_plugins:
            dat.append([p,
                        p in self.enabled_plugins,
                        p in fnames])
        return list2table(dat, header=['name', 'enabled', 'installed'])

class Plugin(SmashPlugin):
    """ """
    def install(self):
        self.contribute('plugins', PluginInspector())
