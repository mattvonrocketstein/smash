""" smashlib.magics
"""

from IPython.core.magic import Magics, magics_class, line_magic

from smashlib.data import USER_CONFIG_PATH


@magics_class
class SmashMagics(Magics):
    """ main magics for smash """

    @line_magic
    def ed_config(self, parameter_s=''):
        self.shell.magic('ed {0}'.format(USER_CONFIG_PATH))