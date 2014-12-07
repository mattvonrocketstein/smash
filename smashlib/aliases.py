""" smashlib.aliases
"""

from IPython.core.macro import Macro

class AliasMixin(object):
    """ """
    def _get_alias_group(self, group_name):
        return [ self.alias_map.get(group_name, []),
                 self.macro_map.get(group_name, []) ]

    def _load_alias_group(self, group_name):
        aliases, macros = self._get_alias_group(group_name)
        for alias in aliases:
            name, cmd = alias
            self.smash.shell.alias_manager.define_alias(name, cmd)
        self.report("Loaded {0} aliases".format(len(aliases)))

        for m in macros:
            print 'load',m
            name, macro = m
            assert isinstance(macro, basestring)
            macro = 'get_ipython().run_cell("""{0}""")'.format(macro)
            macro = Macro(macro)
            self.smash.shell.user_ns[name]=macro

    def _unload_alias_group(self, group_name):
        aliases, macros = self._get_alias_group(group_name)
        for alias in aliases:
            name, cmd=alias
            try:
                self.smash.shell.alias_manager.undefine_alias(name)
            except ValueError:
                continue
