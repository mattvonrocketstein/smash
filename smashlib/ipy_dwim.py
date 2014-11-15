""" ipy_dwim

    DoWhatIMean
"""
import os
from IPython.utils.traitlets import Bool

from smashlib.v2 import Reporter
from smashlib.util.events import receives_event

class DoWhatIMean(Reporter):
    """ """

    automatic_cd = Bool(
        True, config=True,
        help="cd by just typing directory name")

    automatic_edit = Bool(
        True, config=True,
        help="edit (small) files by just typing filename")

    def init(self):
        pass

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    dwim = DoWhatIMean(ip)
    return dwim

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'
