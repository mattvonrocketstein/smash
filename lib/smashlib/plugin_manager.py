""" smashlib.plugin_manager
"""
import sys
import glob
import tempfile
import os
import json
import shutil
import demjson
import urlparse, urllib
from types import ModuleType

from IPython import ipapi

import smashlib
from smashlib.util import die
from smashlib.util import report,ope
from smashlib.util import die
from smashlib.python import opj, ope, splitext,abspath, ops
from smashlib.reflect import namedAny

ip = ipapi.get()



# plugins can define their own persistent settings, and they
# should be stored here. by default the schema only consists in
# answering whether a plugin is enabled.
DEFAULT_SCHEMA = dict(enabled=0,)


class CommandLineAspect(object):
    def cmdline_enable(self, name, quiet=False):
        ('Enable a plugin by name.  \nThis must be one of the '
         'plugins in ~/.smash/plugins, and you need not specify'
         ' an absolute path.  \n(To move a file or url'
         ' into that directory, use --install.\n')
        if not quiet:
            self.report('enabling {0}'.format(name))
        self._set_enabled(name, 1)

    def cmdline_list(self):
        ("lists and categorizes all available plugins in ~/.smash/plugins.\n")

        plugins     = self.plugin_data
        enabled     = self.enabled_plugins
        disabled    = self.disabled_plugins
        stale       = self.stale_plugins
        if stale:
            self.report('\nstale plugins:')
            for p in stale: print '  ',p
            print
        if enabled:
            self.report('\nenabled plugins:')
            for p in enabled: print '  ',p
            print
        if disabled:
            self.report('\ndisabled plugins:')
            for p in disabled: print '  ',p
        # TODO: staleness
        if not (enabled or disabled):
            self.report('no plugins at all in ' + self.SMASH_DIR)

    def cmdline_install_new_plugin(self, s, opts_enable):
        ('Moves plugin @ "INSTALL" to the smash plugin directory'
         'You can enter a path to a file on disk or a uri.  '
         'There is also support for github gists using '
         'gist://<gist-id>')
        report.plugin_manager('Working on --install on ' + s)
        plugin = None
        success = False
        uris = [ z +'://' for z in 'http https ftp file'.split()]
        if s.startswith('gist://'):
            gist_id = urlparse.urlparse(s).netloc
            tdir = tempfile.gettempdir()
            clone_dir = opj(tdir, gist_id)
            url_t   = 'https://gist.github.com/{0}.git'

            url     = url_t.format(gist_id)
            report.plugin_manager('Cloning gist:')
            self.report('   {0} --> {1}'.format(url,clone_dir))
            __IPYTHON__.magic_pushd(tdir)
            error = os.system('git clone {0}'.format(url))
            if error:
                self.report('failure acquiring gist: could not clone')
            else:
                gist_files = glob.glob(opj(clone_dir, '*.py'))
                if len(gist_files) > 1:
                    self.report('failure acquiring gist: multiple files in gist')
                else:
                    fname = gist_files[0]
                    self.report('Successfully acquired gist: '+fname)
                    __IPYTHON__.magic_popd()
                    plugin_name = os.path.split(fname)[-1]
                    self.report("Plugin name is: "+plugin_name)
                    plugin = self.cmdline_install_new_plugin(fname, opts_enable)
                    self.report("Cleaning " + clone_dir)
                    shutil.rmtree(clone_dir)
                    self.report("Finished installing.")
        elif any([s.startswith(x) for x in uris]):
            try:
                urlparse.urlparse(s)
            except:
                report.plugin_manager('bad url?')
            else:
                fname = s.split('/')[-1].split('?')[0]
                plugin_name = fname
                d = self.PLUGINS_DIR
                fname = opj(d, fname)
                report.plugin_manager('downloading to {0}'.format(fname))
                c = urllib.urlopen(s).read()
                with open(fname,'w') as fhandle:
                    fhandle.write(c)
                success = True
        else:
            s = abspath(s)
            if not ope(s):
                report.ERROR('file does not exist: '+s)
                report.ERROR(' did you mean "smash --enable {0}" ? '.format(s))
                die()
                return None
            if splitext(s)[-1] not in ['.py']:
                report('not implemented yet for '+str(splitext(s)))
                return
            fname = ops(s)[-1]
            plugin_name = fname
            fname = opj(self.PLUGINS_DIR,fname)
            report.plugin_manager('Copying plugin to {0}'.format(fname))
            shutil.copy(s, fname)
            success = True
        if success:
            report.plugin_manager('Plugin acquired successfully.')
            report.plugin_manager('Verifying plugin..')
            try:
                plugin = self.install_plugin_from_fname(fname)
            except Exception,e:
                report.plugin_manager('Giving up, plugin test-install failed.')
                self.report('')
                self.report(str(e))
                self.report('')
                report.plugin_manager('DO NOT use --enable until this is fixed!')
            else:
                report.plugin_manager('Plugin was verified successfully.')

                if opts_enable:
                    report.plugin_manager('Enabling plugin..')
                    self.cmdline_enable(plugin_name,quiet=True)
                    self.report('Plugin was enabled successfully.')
                    self.report('Plugin "{0}" will load the next time '
                                'smash is run.'.format(plugin_name))
                else:
                    self.report('Looks good.. you can use `smash --enable` '
                                'to enable this plugin.')
        if plugin:
            self.report('-'*80)
            plugin_module = getattr(smashlib.active_plugins,
                                    os.path.splitext(plugin_name)[0])
            self.report('\n'+plugin_module.__doc__)
            self.report('-'*80)
        return plugin

class EnumeratingAspect(object):
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

    def _get_some_plugins(self, name, val):
        plugins     = self.plugin_data
        return sorted([ fname for fname in plugins if plugins[fname][name] == val ])


class PluginManager(CommandLineAspect, EnumeratingAspect):
    """ smash plugins manager """

    report = staticmethod(report.plugin_manager)

    def __init__(self):
        self.SMASH_DIR = smashlib._meta['SMASH_DIR']
        self.PLUGINS_DIR = opj(self.SMASH_DIR, 'plugins')
        self.PLUGINS_CONF = opj(self.SMASH_DIR,
                                'etc', 'plugins.json')
        # set these in the global metadata, so anyone can grab it
        smashlib._meta['PLUGINS_DIR'] = self.PLUGINS_DIR
        smashlib._meta['PLUGINS_CONF'] = self.PLUGINS_CONF

        self.plugins_json_file = self.PLUGINS_CONF
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

    def install_plugin_from_plugin_name(self, plugin_name):
        abs_path_to_plugin = opj(self.PLUGINS_DIR, plugin_name)
        if not ope(abs_path_to_plugin):
            report("no such plugin @ "+abs_path_to_plugin)
            die()
        return self.install_plugin_from_fname(abs_path_to_plugin)

    def install_plugin_from_fname(self, abs_path_to_plugin):
        G = globals().copy()
        L = {} #dict(report=self.report)
        G.update(__file__=abs_path_to_plugin,
                 __name__='__smash__')
        execfile(abs_path_to_plugin, G, L)
        G.update(**L)
        if 'Plugin' not in G:
            err  = abs_path_to_plugin + ' is old style,'
            err += ' "Plugin" not found in namespace'
            report.ERROR(err)
            die()
            return None
        rel_fname = os.path.split(abs_path_to_plugin)[-1]
        plugin = G['Plugin']()
        if not isinstance(plugin,SmashPlugin):
            report.ERROR('problem with plugin @ "{0}".'.format(abs_path_to_plugin))
            report.ERROR('  Plugin class was found but does not subclass SmashPlugin.')
            report.ERROR('  to disable this plugin, run: smash --disable {0}'.format(
                rel_fname))
            die()
            return None

        plugin.filename = rel_fname
        plugin.name = getattr(plugin, 'name', rel_fname )
        #plugin.pre_install()
        plugin.install()
        from smashlib import active_plugins
        n = os.path.splitext(abs_path_to_plugin.split(os.path.sep)[-1])[0]
        n = str(n)
        m = ModuleType(n)
        G.pop('__name__')
        for x in G: setattr(m, x, G[x])
        setattr(active_plugins,n,m)
        sys.modules['smashlib.active_plugins.'+n]=m
        self._plugins.append(plugin)
        return plugin

    @property
    def plugin_data(self):
        """ updates based on files in dir and default schema """
        with open(self.plugins_json_file, 'r') as fhandle:
            try:
                from_file = demjson.decode(fhandle.read())
            except demjson.JSONDecodeError:
                err="error reading json file: "+self.plugins_json_file
                report.ERROR(err)
                import sys
                sys.exit(err)
        data = from_file.copy()
        for fname in self.possible_plugins:
            if fname not in data:
                data[fname] = DEFAULT_SCHEMA
        return data

    def install(self):
        """ install all plugins into the running environment """
        for plugin_file in self.enabled_plugins:
            abs_path_to_plugin = os.path.join(self.PLUGINS_DIR, plugin_file)
            if not ope(abs_path_to_plugin):
                msg = ('Your configuration file @ "{0}" contains an error.  '
                       '"{1}" does not exist')
                msg = msg.format(self.plugins_json_file,
                                 abs_path_to_plugin)
                self.report(msg)
                die()
            else:
               try:
                   self.install_plugin_from_fname(abs_path_to_plugin)
               except Exception, e:
                   self.report("ERROR loading plugin @ `" + \
                               plugin_file+'`. Exception follows:')
                   self.report('Exception: ')
                   print str([type(e), e])
                   raise

        #FIXME: cleaner way to do this back-ref
        smashlib.PLUGINS = self._plugins
        return smashlib.PLUGINS

from .smash_plugin import SmashPlugin
