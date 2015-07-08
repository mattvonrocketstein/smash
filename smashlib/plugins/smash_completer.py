""" smashlib.plugins.smash_completer
"""
import keyword
import os
from smashlib.plugins import Plugin
from smashlib.util.ipy import have_command_alias
from smashlib._logging import smash_log
from smashlib import get_smash

from IPython.core.completerlib import TryNext
from smashlib.bin.pybcompgen import complete


def smash_bash_complete(*args, **kargs):
    smash_log.info("calling pybcompgen")
    result = complete(*args, **kargs)
    result = [x for x in result if x not in keyword.kwlist]
    return result


def smash_env_complete(symbol):
    smash_log.info("symbol: [{0}]".format(symbol))
    if symbol.startswith('$'):
        symbol = symbol[1:]
    return [x for x in os.environ if x.startswith(symbol)]


class SmashCompleter(Plugin):

    verbose = True
    MAX_SIZE = 3
    MAX_MATCH = 5
    db = []

    def init(self):
        smash_log.debug('initializing')
        self.contribute_completer('.*', self.smash_matcher)

    def smash_matcher(self, shell, event):
        smash_log.info('completing event: {0}'.format(event.__dict__))
        line = event.line

        if not line.strip():
            raise TryNext()
        first_word = line.split()[0]
        # cannot use event.symbol splits on '$'
        last_word = line.split()[-1]
        if last_word.startswith('$'):
            return smash_env_complete(last_word)
        magic_command_alias = first_word.startswith('%') and \
            have_command_alias(first_word[1:])
        naked_command_alias = have_command_alias(first_word)
        if naked_command_alias:
            return smash_bash_complete(line)[:self.MAX_MATCH]
        if magic_command_alias:
            return smash_bash_complete(line[1:])[:self.MAX_MATCH]
        raise TryNext()


def load_ipython_extension(ip):
    ip = get_smash().shell
    return SmashCompleter(ip).install()
