""" smashlib.plugins.interface
    NB: plugin-related obviously, but this is not a plugin
"""

from report import console

from smashlib import get_smash
from smashlib.handle import AbstractInterface


class PluginInterface(AbstractInterface):

    _user_ns_var = 'plugins'

    @property
    def edit(self):
        get_smash().shell.run_cell('ed_config')

    def __qmark__(self):
        """ user-friendly information when the input is "plugins?" """
        out = [console.red('Smash Plugins: ') + '({0} total)'.format(len(self._plugins))]
        for nick in sorted(self._plugins):
            out += [console.blue('   | ') + '{0}'.format(nick)]
        return '\n'.join(out)

    @property
    def _plugins(self):
        return get_smash()._installed_plugins

    def __getitem__(self, plugin_name):
        return self._plugins[plugin_name]

    def update(self):
        tmp = self._plugins

        for name in tmp:
            tmp2 = lambda self=self, name=name: get_smash()._installed_plugins[
                name]
            tmp3 = get_smash()._installed_plugins[name].__qmark__()
            tmp2.__doc__ = tmp3
            prop = property(tmp2)
            setattr(self.__class__, name, prop)
