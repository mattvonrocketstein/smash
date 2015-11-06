""" smashlib.scheduler
"""

import time
import threading

from schedule import default_scheduler
from smashlib._logging import smash_log

wait_interval = .7

class Scheduler(object):
    """ """

    def __init__(self, smash):
        self.smash = smash
        self.scheduler = default_scheduler
        self.ask_stop = False

    def iterate(self):
        report_count = 30
        count=0
        while not self.ask_stop:
            count+=1
            time.sleep(wait_interval)
            if count >= report_count:
                smash_log.info('running scheduler')
                count = 0
            self.scheduler.run_pending()
        smash_log.info('scheduler stopping')

    def start(self):
        self.refresh_scheduler()
        thread = threading.Thread(target=self.iterate)
        thread.start()
        smash_log.info('scheduler started')
        return thread

    def stop(self):
        self.ask_stop = True

    def refresh_scheduler(self):
        reload_task = self.smash.project_manager.reload
        self.scheduler.every(5).seconds.do(reload_task)
