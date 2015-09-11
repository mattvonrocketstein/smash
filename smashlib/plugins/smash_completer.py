""" smashlib.plugins.smash_completer
"""
import os
import keyword

from smashlib import get_smash
from smashlib.plugins import Plugin
from smashlib.util.ipy import have_command_alias
from smashlib._logging import smash_log, completion_log
from smashlib.bin.pybcompgen import complete

from IPython.core.completerlib import TryNext


def smash_bash_complete(*args, **kargs):
    smash_log.info("calling pybcompgen: {0}".format([args, kargs]))
    result = complete(*args, **kargs)
    smash_log.info("result: {0}".format(result))
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
        super(SmashCompleter, self).init()
        self.contribute_completer('.*', self.smash_matcher)

    def smash_matcher(self, shell, event):
        completion_log.info('completing event: {0}'.format(event.__dict__))
        line = event.line

        if not line.strip():
            raise TryNext()
        first_word = line.split()[0]
        # NB: cannot use event.symbol here, it splits on '$'
        last_word = event.text_until_cursor.split()
        last_word = last_word[-1] if last_word else ''
        completion_log.info("first-word, last-word: {0}".format(
            [first_word, last_word]))
        if last_word.startswith('$'):
            return smash_env_complete(last_word)
        magic_command_alias = first_word.startswith('%') and \
            have_command_alias(first_word[1:])
        naked_command_alias = have_command_alias(first_word)
        results = []
        if naked_command_alias:
            completion_log.info('naked command alias detected')
            results += smash_bash_complete(line)[:self.MAX_MATCH]
        elif magic_command_alias:
            completion_log.info('magic command alias detected')
            results += smash_bash_complete(line[1:])[:self.MAX_MATCH]

        # can't do anything smarter? look for file matches.
        # this works by default if the last word contains os.path.sep,
        # but this doesn't necessarily work with the special "ed" alias
        # unless this sectiion is executed
        if not results:
            completion_log.info(('no results for completion, looking for '
                                 'file matches with "{0}"'.format(last_word)))
            results = self.smash.shell.Completer.file_matches(last_word)

        if results:
            completion_log.info("returning: {0}".format(results))
            return results
        else:
            completion_log.info("no results so far, raising trynext ")
            raise TryNext()


def load_ipython_extension(ip):
    ip = get_smash().shell
    return SmashCompleter(ip).install()
