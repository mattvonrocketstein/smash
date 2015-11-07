""" smashlib.aliases
"""

from IPython.core.macro import Macro

from report import console

from smashlib.handle import AbstractInterface
from smashlib._logging import smash_log
from smashlib import get_smash

class AliasMixin(object):

    """ """

    def _get_alias_group(self, group_name):
        return [self.alias_map.get(group_name, []),
                self.macro_map.get(group_name, [])]

    def _load_macro(self, macro, name=None):
        smash_log.debug('[{0}]'.format(dict(macro=macro, name=name)))
        assert isinstance(macro, basestring)
        macro = 'get_ipython().run_cell("""{0}""")'.format(macro)
        macro = Macro(macro)
        get_smash().shell.user_ns[name] = macro

    def _load_alias_group(self, group_name):
        smash_log.info('loading alias group: {0}'.format(group_name))
        aliases, macros = self._get_alias_group(group_name)
        for alias in aliases:
            name, cmd = alias
            get_smash().shell.alias_manager.define_alias(name, cmd)
            smash_log.info(' alias: {0}'.format(name))
        self.report("Loaded {0} aliases".format(len(aliases)))

        for m in macros:
            name, macro = m
            self._load_macro(macro, name=name)

    def _unload_alias_group(self, group_name):
        smash_log.info('unloading alias group: {0}'.format(group_name))
        aliases, macros = self._get_alias_group(group_name)
        for alias in aliases:
            name, cmd = alias
            try:
                get_smash().shell.alias_manager.undefine_alias(name)
            except ValueError:
                continue


class AliasInterface(AbstractInterface):

    _user_ns_var = 'aliases'

    def __qmark__(self):
        """ user-friendly information when the input is "plugins?" """
        alias_map = get_smash().project_manager.alias_map
        out = [console.red('Smash Aliases:') + ' ({0} total, {1} groups)'.format(
            len(self._aliases),
            len(alias_map))]
        for group_name in alias_map.keys():
            g_aliases = alias_map[group_name]
            max_summary = 3
            summary = [x[0] for x in g_aliases[:max_summary]]
            if len(g_aliases) > max_summary:
                summary += ['..']
            summary = ', '.join(summary)
            out += ['   : "{0}" with {1} aliases: {2})'.format(
                group_name, len(g_aliases), summary)]

        return '\n'.join(out)

    @property
    def edit(self):
        get_smash().shell.run_cell('ed_aliases')

    @property
    def _aliases(self):
        return [x[0].replace('-', '.') for x in get_smash().shell.alias_manager.aliases]

    def zonk(self,  name):
        def blue(himself):
            return get_smash().shell.alias_manager.linemagics.get(name)
        return blue

    def update(self):
        tmp = self._aliases
        for name in tmp:
            tmp2 = self.zonk(name)
            tmp3 = "testinge7e9d3a8-5845-11e5-901b-0800272dfc6a"
            # get_smash()._installed_aliases[name].__qmark__()
            tmp2.__doc__ = tmp3
            prop = property(tmp2)
            setattr(self.__class__, name, prop)


def fxn(self, name):
    return get_smash().shell.alias_manager.linemagics.get(name)
