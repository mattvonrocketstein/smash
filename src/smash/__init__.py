"""
"""
import os
import demjson
from IPython import ipapi
from smash.util import report

ip = ipapi.get()

class Plugins(object):
    report = staticmethod(report.plugins)

    def __init__(self, SMASH_DIR):
        self.SMASH_DIR=SMASH_DIR
        self.plugins_json_file = os.path.join(SMASH_DIR, 'plugins.json')


    def _set_enabled(self, name, val):
        data = self.plugin_data
        assert name in data,"Bad plugin?"
        data[name] = val
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
        with open(self.plugins_json_file, 'r') as fhandle:
            from_file = demjson.decode(fhandle.read())
        data = from_file.copy()
        for fname in self.possible_plugins:
            if fname not in data:
                data[fname] = 0
        return data

    @property
    def possible_plugins(self):
        return [ fname for fname in os.listdir(self.SMASH_DIR) if fname.endswith('.py') ]

    def install(self):
        """ """
        # loop thru just enabled plugins
        for plugin_file in self._get_enabled_plugins():
            abs_path_to_plugin = os.path.join(self.SMASH_DIR, plugin_file)
            assert os.path.exists(abs_path_to_plugin)
            try:
                plugin_module = ''#__import__(os.path.splitext(plugin_file)[0])
                G = globals().copy()
                L = dict(report=self.report)
                G.update(__name__='__smash__')
                execfile(abs_path_to_plugin, G, L)
            except Exception,e:
                self.report("ERROR loading plugin @ `" + plugin_file+'`. Exception follows:')
                self.report('Exception: '+ str([type(e),e]))
                raise
            else:
                self.report('installed '+plugin_file+' ok')
                #\n{0}'.format(plugin_module.__doc__))

    def _get_enabled_plugins(self):
        plugins     = self.plugin_data
        enabled     = [ fname for fname in plugins if plugins[fname] == 1 ]
        return enabled

    def list(self, enabled=True, disabled=True):
        """ lists available plugins (from {0}) """.format(self.SMASH_DIR)
        # reconstructed because `plugins_json_file` may not be up to date with system
        plugins     = self.plugin_data
        enabled     = self._get_enabled_plugins()
        disabled    = disabled and [ fname for fname in plugins if plugins[fname] == 0 ]

        if enabled:
            self.report('enabled plugins')
            for p in enabled: print '  ',p
            print
        if disabled:
            self.report('disabled plugins:')
            for p in disabled: print '  ',p

        if not (enabled or disabled):
            self.report('no plugins at all in ' + self.SMASH_DIR)

        if enabled and not disabled: return enabled
        if disabled and not enabled: return disabled
