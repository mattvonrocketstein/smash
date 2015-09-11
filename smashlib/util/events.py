""" smashlib.util.events
"""

from functools import wraps

from smashlib import get_smash
from smashlib.util.ipy import TermColors
from smashlib._logging import smash_log, events_log


class receives_event(object):

    """ note: should only be used with imethods """

    def __init__(self, channel, quiet=False):
        self.channel = channel
        self.quiet = quiet

    def report(self, args):
        fxn = self.fxn
        zargs = args[0] if len(args) == 1 else args
        msg = '{0}!{1}{2} @ "{3}" = {4}'.format(
            TermColors.LightPurple,
            self.channel,
            TermColors.Normal,
            fxn.__name__,
            zargs)
        if msg[:77] != msg:
            msg += '...'
            msg = msg[:77]
        events_log.info(msg)

    def __call__(self, fxn):
        self.fxn = fxn

        @wraps(fxn)
        def receive_events_wrapper(himself, bus, *args, **kargs):
            events_log.info('{0}'.format(str(args)))
            return fxn(himself, *args, **kargs)
        receive_events_wrapper._subscribe_to = self.channel
        return receive_events_wrapper
