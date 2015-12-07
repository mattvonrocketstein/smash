""" smashlib.scheduler
"""

import time
import threading

from schedule import default_scheduler
from smashlib._logging import scheduler_log
from smashlib import get_smash

WAIT_INTERVAL = .7
REPORT_COUNT = 30
SMALL_RUN_INTERVAL = 5

class Scheduler(object):
    """ thin wrapper around `schedule` library functionality """

    def __init__(self):
        self.scheduler = default_scheduler
        self.ask_stop = False

    def __repr__(self):
        return '<SmashScheduler: {0}>'.format(
            repr(self.scheduler.jobs))
    __str__ = __repr__

    def run_continuously(self):
        """ main loop for scheduler """
        count = 0
        while not self.ask_stop:
            if not get_smash():
                scheduler_log.info('smash not ready')
                continue
            count += 1
            time.sleep(WAIT_INTERVAL)
            if count >= REPORT_COUNT:
                scheduler_log.info(str(self))
                count = 0
            self.scheduler.run_pending()
        scheduler_log.info('scheduler stopping')

    def start(self):
        """ stop the smash scheduler """
        thread = threading.Thread(target=self.run_continuously)
        thread.start()
        scheduler_log.info('scheduler started')
        return thread

    def add(self, fxn, interval=SMALL_RUN_INTERVAL):
        """ add a function to the scheduler """
        msg = "registering function {0} with interval {1}"
        scheduler_log.info(msg.format(fxn, interval))
        self.scheduler.every(interval).seconds.do(fxn)

    def stop(self):
        """ stop the smash scheduler """
        scheduler_log.info("asking for stop")
        self.ask_stop = True
scheduler = Scheduler()
