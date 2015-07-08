""" smashlib.plugins.history_completer
"""
from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_POST_RUN_INPUT
from smashlib._logging import smash_log
from smashlib import get_smash

from goulash.python import splitext, ops
from goulash.parsing import smart_split
from goulash.set import OrderedSet
from IPython.core.completerlib import TryNext


class HistoryCompleter(Plugin):

    verbose = True
    MAX_SIZE = 3
    MAX_MATCH = 5
    db = []

    def init(self):
        smash_log.debug('initializing')
        #self.smash.shell.Completer.matchers += [self.history_matcher]
        self.contribute_completer('.*', self.history_matcher)

    def history_matcher(self, shell, event):
        """ """
        #print ('event: {0}'.format(event.__dict__))
        smash_log.info('invoked')
        # event attributes: text_until_cursor, line, command, symbol
        #smash_log.debug('matching {0}'.format(event.__dict__))
        if not event.symbol.strip():
            raise TryNext()
        tmp = [x for x in self.db if x.startswith(event.symbol)]
        if not tmp:
            raise TryNext()
        else:
            return tmp[:self.MAX_MATCH]

    @receives_event(C_POST_RUN_INPUT, quiet=True)
    def history_completion_update(self, line):
        smash_log
        line = line.strip()
        tokens = smart_split(line)
        full = len(self.db) > self.MAX_SIZE
        #smash_log.info('eating [{0}]'.format(tokens))
        for token in tokens:
            if len(token) < 4:
                # too small, dont care
                continue
            self.db.append(token)
            smash_log.info('eating token: {0}'.format(token))
            if full:
                self.db.pop(0)


def load_ipython_extension(ip):
    ip = get_ipython()
    return HistoryCompleter(ip).install()
