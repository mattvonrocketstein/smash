""" smashlib.plugins.dwim

    documentation: http://mattvonrocketstein.github.io/smash/plugins.html#dwim
"""
import datetime


from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_POST_RUN_CELL, C_PRE_RUN_CELL

now = datetime.datetime.now
timedelta = datetime.timedelta

class TimeLongCommands(Plugin):

    """ """

    verbose = True
    timer_data = None
    threshhold = timedelta(seconds=5)

    @receives_event(C_PRE_RUN_CELL)
    def start_timer(self, cmd):
        self.timer_data = datetime.datetime.now()

    @receives_event(C_POST_RUN_CELL)
    def stop_timer(self, *args):
        difference = now()-self.timer_data
        if self.threshhold < difference:
            self.report("total time: {0}".format(difference))
        self.timer_data = None

    #def init(self):

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return TimeLongCommands(get_ipython()).install()
