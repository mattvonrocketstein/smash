""" smashlib.magics
"""

from IPython.core.magic import Magics, magics_class, line_magic

from smashlib.data import USER_CONFIG_PATH, EDITOR_CONFIG_PATH
from smashlib.data import ALIAS_CONFIG_PATH, MACRO_CONFIG_PATH


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
    def ed_macros(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(ALIAS_CONFIG_PATH))

    @line_magic
    def ed_editor(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(EDITOR_CONFIG_PATH))
