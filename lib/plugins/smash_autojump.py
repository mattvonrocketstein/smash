""" smash_autojump
"""

import smashlib
from smashlib.util import report, report_if_verbose
from smashlib.smash_plugin import SmashPlugin
#from smashlib.contrib.autojump import Database
data_file = 'autojump.dat'

class Plugin(SmashPlugin):
    def install(self):
        df = opj(smashlib._meta['SMASH_DIR'], data_file)
        report('this is it' + df)
        #Database(df)
