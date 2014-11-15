""" ipy_dwim

    DoWhatIMean
"""
import os
from IPython.utils.traitlets import Bool
from IPython.config.configurable import Configurable

from smashlib.v2 import Reporter


class DoWhatIMean(Reporter):
    """ """

    verbose=True

    automatic_cd = Bool(
        True, config=True,
        help="change directory if input looks like path name")
    automatic_edit = Bool(
        True, config=True,
        help="edit (small) files if input looks like file name")
    automatic_connect = Bool(
        True, config=True,
        help="connect automatically if input matches something in hosts-file")
    automatic_open = Bool(
        True, config=True,
        help="open automatically if input looks like webpage")

    def init(self):
        if self.automatic_cd or self.automatic_edit:
            self.smash.error_handlers.append(self.handle_NameError)

    def handle_NameError(self, last_line, etype, evalue):
        if etype!=NameError:
            return

        line = last_line
        if len(line.split())==1 and os.path.exists(line):
            if self.automatic_cd and os.path.isdir(line):
                self.report('cd '+line)
                self.smash.shell.magic('pushd '+line)
            else:
                flimit = 712020
                if flimit < os.path.getsize(line):
                    msg = ("warning: maybe you wanted to edit"
                           " that file but it looks big")
                    self.report(msg)
                else:
                    self.report('ed '+line)
                    self.smash.shell.magic('ed '+line)
            return True

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    dwim = DoWhatIMean(ip)
    return dwim

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'
