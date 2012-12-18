""" pkill_completer

      tab-completer for unix kill commands
"""

import signal

import psutil

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report, set_complete

def proc_name_completer(self, event):
    procs = set([x.name for x in psutil.process_iter() \
                 if ' ' not in x.name and \
                 '/' not in x.name and \
                 ':' not in x.name ])
    return procs

def signal_completer(self, event):
    return [ '-'+x[3:] for x in dir(signal) if x.startswith('SIG') ]

class Plugin(SmashPlugin):
    def install(self):
        set_complete(proc_name_completer, 'pkill')
        set_complete(signal_completer, 'kill')
        #set_complete(proc_pid_completer, 'kill -KILL')
