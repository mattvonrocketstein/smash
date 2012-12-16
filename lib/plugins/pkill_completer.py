""" pkill_completer
"""

import psutil

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import report, set_complete

def proc_name_completer(self, event):
    procs = set([x.name for x in psutil.process_iter() \
                 if ' ' not in x.name and \
                 '/' not in x.name and \
                 ':' not in x.name ])

    return procs

class Plugin(SmashPlugin):
    def install(self):
        set_complete(proc_name_completer, 'pkill')
