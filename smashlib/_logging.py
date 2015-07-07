""" smashlib._logging
"""
import os
import logging
from logging.config import dictConfig

from goulash.python import ope, opj, dirname

from smashlib.data import SMASH_LOGS
from goulash._os import touch_file
from IPython.utils.coloransi import TermColors

default_file = opj(SMASH_LOGS, 'smash.log')
event_file = opj(SMASH_LOGS, 'events.log')
#boot_file = opj(SMASH_LOGS, 'bootstrap.log')

if not ope(SMASH_LOGS):
    os.makedirs(SMASH_LOGS)
touch_file(default_file)
touch_file(event_file)
LOG_FMT = ('[%(name)s:%(levelname)s:%(process)d] '
           '%(pathname)s:%(lineno)-4d'
           ' - %(funcName)s: %(message)s')

LOG_SETTINGS = {
    'version': 1,
    'handlers': {
        # 'console': {
        #     'class': 'logging.StreamHandler',
        #     'level': 'DEBUG',
        #     'formatter': 'detailed',
        #     'stream': 'ext://sys.stdout',},
        'event_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': event_file,
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5, },
        'default_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': default_file,
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5, },
    },
    'formatters': {
        'detailed': {
            'format': LOG_FMT,
        },
    },
    'loggers': {
        'smash': {
            'level': 'DEBUG',
            'handlers': ['default_file', ]
        },
    }
}

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
