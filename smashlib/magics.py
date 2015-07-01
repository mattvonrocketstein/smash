""" smashlib.magics
"""
from IPython.core.magic import Magics, magics_class, line_magic

from smashlib import get_smash
from smashlib.data import USER_CONFIG_PATH, EDITOR_CONFIG_PATH
from smashlib.data import ALIAS_CONFIG_PATH, MACRO_CONFIG_PATH
from smashlib.data import ENV_CONFIG_PATH, PROMPT_CONFIG_PATH


@magics_class
class SmashMagics(Magics):

    """ main magics for smash """

    @line_magic
    def ed_config(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(USER_CONFIG_PATH))

    @line_magic
    def ed_aliases(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(ALIAS_CONFIG_PATH))

    @line_magic
    def ed_env(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(ENV_CONFIG_PATH))

    @line_magic
    def ed_prompt(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(PROMPT_CONFIG_PATH))

    @line_magic
    def ed_macros(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(MACRO_CONFIG_PATH))

    @line_magic
    def ed_editor(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(EDITOR_CONFIG_PATH))

    @line_magic
    def uninstall_plugin(self, parameter_s=""):
        plugin_name = parameter_s.strip().split()[-1]
        get_smash()._installed_plugins[plugin_name].uninstall()
