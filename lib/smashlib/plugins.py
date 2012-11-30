""" smashlib.plugins
"""
import os
import json
import demjson
from IPython import ipapi
from smashlib.util import report
from smashlib.python import opj, ope

ip = ipapi.get()

DEFAULT_SCHEMA = dict(
    enabled=0,    # 1 for yes, 0 for no
    requires=[],  # list of (relative) fnames for any pre-req plugins
    )

class Plugins(object):
    """ smash plugins manager """

    report = staticmethod(report.plugins)

    def __init__(self):
        import smashlib
        self.SMASH_DIR = smashlib.SMASH_DIR
        self.plugins_json_file = os.path.join(smashlib.SMASH_DIR, 'etc', 'plugins.json')
        self._plugins = []
        if self.stale_plugins:
            data = self.plugin_data
            [ data.pop(fname) for fname in self.stale_plugins ]
            self._update_file(data)

    def _update_file(self, data):
        """ json.dumps(, sort_keys=True, indent=4)
        """
        with open(self.plugins_json_file, 'w') as fhandle:
            fhandle.write(json.dumps(data, sort_keys=True, indent=2))

    def _set_enabled(self, name, val):
        """ helper """
        data = self.plugin_data
        if name not in data:
            print "Bad plugin? {0}".format(name)
            from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        data[name].update(enabled=val)
        self._update_file(data)

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
            raise Exception,abs_path_to_plugin + ' old style.. smash_install function'
        if 'Plugin' not in G:
            raise Exception,abs_path_to_plugin + ' old style, no Plugin'
        plugin = G['Plugin']()
        plugin.install()
        rel_fname = os.path.split(abs_path_to_plugin)[-1]
        if not getattr(plugin, 'name', None):
            plugin.name = rel_fname
        plugin.filename = rel_fname
        self._plugins.append(plugin)

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
        return [ fname for fname in os.listdir(self.PLUGINS_DIR) if fname.endswith('.py') ]
    all_plugins = possible_plugins

    @property
    def enabled_plugins(self):
        """ lists plugins mentioned as enabled in config """
        return self._get_some_plugins('enabled', 1)

    @property
    def disabled_plugins(self):
        """ lists plugins mentioned as disabled in config """
        return self._get_some_plugins('enabled', 0)

    @property
    def stale_plugins(self):
        """ lists plugins mentioned in config but not found on filesystem """
        return set(self.plugin_data.keys())-set(self.possible_plugins)
        stale = []
        for x in self.plugin_data.keys():
            x = opj(self.PLUGINS_DIR, x)
            if not ope(x):
                stale.append(x)
        return stale

    def list(self):
        """ lists available plugins (from {0}) """.format(self.SMASH_DIR)
        # reconstructed because `plugins_json_file` may not be up to date with system
        plugins     = self.plugin_data
        enabled     = self.enabled_plugins
        disabled    = self.disabled_plugins

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
                msg = ('Your configuration file @ "{0}" contains an error.  '
                       '"{1}" does not exist')
                from smashlib.util import die
                self.report(msg.format(self.plugins_json_file,
                                       abs_path_to_plugin))
                die()
            try:
                self.install_plugin_from_fname(abs_path_to_plugin)
            except Exception, e:
                self.report("ERROR loading plugin @ `" + plugin_file+'`. Exception follows:')
                self.report('Exception: ')
                print str([type(e),e])
                raise
            #else:
            #    self.report('installed '+plugin_file+' ok')

        #FIXME: cleaner way to do this back-ref
        import smashlib
        smashlib.PLUGINS = self._plugins

class SmashPlugin(object):
    """ TODO: ... """

    requires = []

    def __repr__(self):
        return '<SmashPlugin@"{0}">'.format(self.name)

    def verify_requirements(self):
        report('pretending to verify requirements: {0}'.format(self.requires))

    def install_into_smash(self):
        """ install this plugin into the smash shell """
        self.verify_requirements()
        self.install()

    def contribute(self,name,val):
        """ contribute name/val to IPython shells' namespace """
        if name in __IPYTHON__.user_ns:
            msg = ('"{0}" variable is taken in user namespace.  '
                   'refusing to proceed').format(name)
            report.plugin(msg)
        else:
            __IPYTHON__.user_ns.update(**{name:val})
            msg = ("finished installing.  "
                   "type '{0}?' for help with search").format(name)
            report.plugin(msg)

    def contribute_magic(self, name, func):
        if name.startswith('magic_'):
            magic_name = name
        else:
            magic_name = 'magic_{0}'.format(name)
        setattr(__IPYTHON__, magic_name, func)
        return func
