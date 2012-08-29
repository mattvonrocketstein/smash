"""
"""
import os
import demjson
from collections import defaultdict
from IPython import ipapi
from smash.util import report

ip = ipapi.get()
DEFAULT_SCHEMA = dict(
    enabled=0,    # 1 for yes, 0 for no
    requires=[],  # list of other plugins it needs
    )

class Plugins(object):
    report = staticmethod(report.plugins)

    def __init__(self, SMASH_DIR):
        self.SMASH_DIR=SMASH_DIR
        self.plugins_json_file = os.path.join(SMASH_DIR, 'plugins.json')

    def _set_enabled(self, name, val):
        data = self.plugin_data
        assert name in data,"Bad plugin?"
        data[name].update(enabled=val)
        with open(self.plugins_json_file,'w') as fhandle:
            fhandle.write(demjson.encode(data))

    def disable(self, name):
        """ disable plugin by name """
        self.report('disabling {0}'.format(name))
        self._set_enabled(name, 0)

    def enable(self, name):
        """ enable plugin by name """
        self.report('enabling {0}'.format(name))
        self._set_enabled(name, 1)

    @property
    def plugin_data(self):
        """ updates based on files in dir and default schema """
        with open(self.plugins_json_file, 'r') as fhandle:
            from_file = demjson.decode(fhandle.read())
        data = from_file.copy()
        for fname in self.possible_plugins:
            if fname not in data:
                data[fname] = DEFAULT_SCHEMA
        return data

    @property
    def possible_plugins(self):
        return [ fname for fname in os.listdir(self.SMASH_DIR) if fname.endswith('.py') ]

    def install_plugin_from_fname(self, abs_path_to_plugin):
        G = globals().copy()
        L = dict(report=self.report)
        G.update(__name__='__smash__')
        execfile(abs_path_to_plugin, G, L)
        G.update(**L)
        if 'smash_install' in G :
            G['smash_install']()

    def install(self):
        """ """
        for plugin_file in self._get_enabled_plugins():
            abs_path_to_plugin = os.path.join(self.SMASH_DIR, plugin_file)
            assert os.path.exists(abs_path_to_plugin)
            try:
                self.install_plugin_from_fname(abs_path_to_plugin)
            except Exception,e:
                self.report("ERROR loading plugin @ `" + plugin_file+'`. Exception follows:')
                self.report('Exception: '+ str([type(e),e]))
                raise
            else:
                self.report('installed '+plugin_file+' ok')
        import smash
        smash.PLUGINS = self

    def _get_some_plugins(self, name, val):
        plugins     = self.plugin_data
        return [ fname for fname in plugins if plugins[fname][name] == val ]

    def _get_enabled_plugins(self):
        return self._get_some_plugins('enabled', 1)

    def _get_disabled_plugins(self):
        return self._get_some_plugins('enabled', 0)

    def list(self):
        """ lists available plugins (from {0}) """.format(self.SMASH_DIR)
        # reconstructed because `plugins_json_file` may not be up to date with system
        plugins     = self.plugin_data
        enabled     = self._get_enabled_plugins()
        disabled     = self._get_disabled_plugins()

        if enabled:
            self.report('enabled plugins')
            for p in enabled: print '  ',p
            print
        if disabled:
            self.report('disabled plugins:')
            for p in disabled: print '  ',p
        if not (enabled or disabled):
            self.report('no plugins at all in ' + self.SMASH_DIR)
