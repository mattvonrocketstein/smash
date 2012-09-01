""" smash.plugins
"""
import os
import demjson
from collections import defaultdict

from IPython import ipapi
from smash.util import report

ip = ipapi.get()

DEFAULT_SCHEMA = dict(
    enabled=0,    # 1 for yes, 0 for no
    requires=[],  # list of (relative) fnames for any pre-req plugins
    )

class Plugins(object):
    """ smash plugins manager """
    report = staticmethod(report.plugins)

    def __init__(self, SMASH_DIR):
        self.SMASH_DIR = SMASH_DIR
        self.plugins_json_file = os.path.join(SMASH_DIR, 'plugins.json')

    def _set_enabled(self, name, val):
        """ helper """
        data = self.plugin_data
        if name not in data:
            print "Bad plugin? {0}".format(name)
            from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
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

    def install_plugin_from_fname(self, abs_path_to_plugin):
        G = globals().copy()
        L = dict(report=self.report)
        G.update(__name__='__smash__')
        execfile(abs_path_to_plugin, G, L)
        G.update(**L)
        if 'smash_install' in G :
            G['smash_install']()

    def _get_some_plugins(self, name, val):
        plugins     = self.plugin_data
        return [ fname for fname in plugins if plugins[fname][name] == val ]

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
        return [ fname for fname in os.listdir(os.path.join(self.SMASH_DIR, 'plugins')) if fname.endswith('.py') ]

    @property
    def enabled_plugins(self):
        return self._get_some_plugins('enabled', 1)

    @property
    def disabled_plugins(self):
        return self._get_some_plugins('enabled', 0)

    def list(self):
        """ lists available plugins (from {0}) """.format(self.SMASH_DIR)
        # reconstructed because `plugins_json_file` may not be up to date with system
        plugins     = self.plugin_data
        enabled     = self.enabled_plugins
        disabled     = self.disabled_plugins

        if enabled:
            self.report('enabled plugins')
            for p in enabled: print '  ',p
            print
        if disabled:
            self.report('disabled plugins:')
            for p in disabled: print '  ',p
        if not (enabled or disabled):
            self.report('no plugins at all in ' + self.SMASH_DIR)

    @property
    def PLUGINS_DIR(self):
        return os.path.join(self.SMASH_DIR, 'plugins')

    def install(self):
        """ install all plugins into the running environment """
        for plugin_file in self.enabled_plugins:
            abs_path_to_plugin = os.path.join(self.PLUGINS_DIR, plugin_file)
            if not os.path.exists(abs_path_to_plugin):
                raise ValueError,'{0} does not exist'.format(abs_path_to_plugin)
            try:
                self.install_plugin_from_fname(abs_path_to_plugin)
            except Exception,e:
                self.report("ERROR loading plugin @ `" + plugin_file+'`. Exception follows:')
                self.report('Exception: ')
                print str([type(e),e])
                raise
            else:
                self.report('installed '+plugin_file+' ok')

        #FIXME: cleaner way to do this back-ref
        import smash
        smash.PLUGINS = self