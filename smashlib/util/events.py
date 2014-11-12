""" smashlib.util.events
"""
from smashlib.util import get_smash
from smashlib.util.ipy import TermColors

class receives_event(object):
    """ note: should only be used with imethods """
    def __init__(self, channel):
        self.channel = channel

    def __call__(self, fxn):
        def newf(himself, bus, *args, **kargs):
            if get_smash().verbose_events:
                zargs=args[0] if len(args)==1 else args
                msg = '{0}!{1}{2} @{3} ={4}'.format(
                    TermColors.LightPurple,
                    self.channel,
                    TermColors.Normal,
                    fxn.__name__,
                    zargs)
                if msg[:77]!=msg:
                    msg += '...'
                    msg=msg[:77]
                print msg
            return fxn(himself, *args, **kargs)
        newf._subscribe_to = self.channel
        return newf
