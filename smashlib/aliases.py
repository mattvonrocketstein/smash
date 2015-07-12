""" smashlib.aliases
"""

from IPython.core.macro import Macro
from peak.util.imports import lazyModule
from smashlib.handle import AbstractInterface

logging = lazyModule('smashlib._logging')


class AliasMixin(object):

    """ """

    def _get_alias_group(self, group_name):
        return [self.alias_map.get(group_name, []),
                self.macro_map.get(group_name, [])]

    def _load_alias_group(self, group_name):
        logging.smash_log.info('loading alias group: {0}'.format(group_name))
        aliases, macros = self._get_alias_group(group_name)
        for alias in aliases:
            name, cmd = alias
            self.smash.shell.alias_manager.define_alias(name, cmd)
            logging.smash_log.info(' alias: {0}'.format(name))
        self.report("Loaded {0} aliases".format(len(aliases)))

        for m in macros:
            print 'load', m
            name, macro = m
            assert isinstance(macro, basestring)
            macro = 'get_ipython().run_cell("""{0}""")'.format(macro)
            macro = Macro(macro)
            self.smash.shell.user_ns[name] = macro

    def _unload_alias_group(self, group_name):
        logging.smash_log.info('unloading alias group: {0}'.format(group_name))
        aliases, macros = self._get_alias_group(group_name)
        for alias in aliases:
            name, cmd = alias
            try:
                self.smash.shell.alias_manager.undefine_alias(name)
            except ValueError:
                continue


class AliasInterface(AbstractInterface):

    user_ns_var = 'aliases'

    def __qmark__(self):
        """ user-friendly information when the input is "plugins?" """
        alias_map = self.smash.project_manager.alias_map
        out = ['Smash Aliases: ({0} total, {1} groups)'.format(
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
        self.smash.shell.run_cell('ed_aliases')

    @property
    def _aliases(self):
        return [x[0].replace('-', '.') for x in self.smash.shell.alias_manager.aliases]

    def zonk(self,  name):
        def blue(himself):
            return self.smash.shell.alias_manager.linemagics.get(name)
        return blue

    def update(self):
        tmp = self._aliases
        for name in tmp:
            tmp2 = self.zonk(name)
            tmp3 = "zoo"  # self.smash._installed_aliases[name].__qmark__()
            tmp2.__doc__ = tmp3
            prop = property(tmp2)
            setattr(self.__class__, name, prop)


def fxn(self, name):
    return self.smash.shell.alias_manager.linemagics.get(name)
