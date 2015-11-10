""" smashlib._logging
"""
import os
import logging
from logging.config import dictConfig

from goulash.python import ope


from smashlib.data import (
    D_SMASH_LOGS, LOG_HANDLER_DEFAULTS, LOG_FORMAT_DEFAULT)
from goulash._os import touch_file
from IPython.utils.coloransi import TermColors

if not ope(D_SMASH_LOGS):
    os.makedirs(D_SMASH_LOGS)

def _get_file(_name):
    log_file = os.path.join(D_SMASH_LOGS, '{0}.log'.format(_name))
    touch_file(log_file)
    return log_file

def _get_handler(_file):
    _handler = LOG_HANDLER_DEFAULTS.copy()
    _handler['filename'] = _file
    return _handler

#Empty string here corresponds to default (smash.log)
MAIN_LOGS = ['', 'events','scheduler', 'completion']

LOG_HANDLERS = dict([
    ['smash_'+x if x else 'smash', _get_handler(_get_file(x if x else 'smash'))] \
    for x in MAIN_LOGS ])
LOG_LOGGERS = dict([
    ['smash_'+x if x else 'smash',
     {'level': 'DEBUG',
      'handlers': ['smash_'+x if x else 'smash',]}] \
    for x in MAIN_LOGS ])
LOG_SETTINGS = dict(
    version= 1,
    formatters= {'detailed': {'format': LOG_FORMAT_DEFAULT, },},
    handlers = LOG_HANDLERS,
    loggers = LOG_LOGGERS,
    )

last_change = None
def reset_logs():
    def ignoreHandlers(*args, **kargs):
        from goulash._inspect import get_caller
        caller_context = get_caller(4)
        global last_change
        last_change = caller_context
        print 'LOGGING SETUP CHANGED BY:', caller_context['__file__']
    # instantiate root logger & remove all old handlers
    log = logging.getLogger()
    for hdlr in log.handlers:
        log.removeHandler(hdlr)
    # this is insane, but some module somewhere is badly behaved
    # and keeps adding a handler after my initialization.  this
    # results in lots of noise going to stdout.  let everything
    # use it's own logger, and let nothing use the root logger
    log.addHandler = ignoreHandlers
    return log

dictConfig(LOG_SETTINGS)
log = reset_logs()
smash_log = logger = logging.getLogger('smash')
completion_log = logging.getLogger('smash_completion')
events_log = logging.getLogger('smash_events')
scheduler_log = logging.getLogger('smash_scheduler')
logger.info("Initializing smash default logger")


class Logger(object):

    def __init__(self, component):
        self.component = component
        self.info = smash_log.info
        self.debug = smash_log.debug
        self.warning = smash_log.warning
        self.critical = smash_log.critical

    @property
    def verbose(self):
        return self.component.verbose

    def report(self, msg, *args, **kargs):
        force = kargs.pop('force', False)
        if self.verbose or force:
            header = kargs.pop('header', '')
            header = self.component.__class__.__name__ + ':' + header
            header = TermColors.Blue + header
            content = TermColors.Red + msg
            print "{0}: {1} {2}".format(
                header, content, TermColors.Normal)
            if args:
                print '  ', args
