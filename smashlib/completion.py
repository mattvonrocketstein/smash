""" smashlib.completion
"""

import re
import subprocess

def complete_long_opts(cmd):
    """ completes long-opts args for any command,
        assuming it supports --help
    """
    tmp = subprocess.check_output(cmd+' --help',shell=True)
    out = re.compile('\s+--[a-zA-Z]+').findall(tmp)
    out += re.compile('\s+-[a-zA-Z]+').findall(tmp)
    out = [ x.strip() for x in out ]
    out = list(set(out))
    return out

class opt_completer(object):
    """ """
    def __init__(self, cmd_name):
        self.cmd=cmd_name

    def __call__(self, fxn):
        def newf(himself, event):
            line = event.line
            if line and line.split()[-1].startswith('-'):
                return complete_long_opts(self.cmd)
            return fxn(himself, event)
        return newf
