""" smashlib.completion
"""

import re
import subprocess
from smashlib._logging import smash_log
from smashlib.util.ipy import have_command_alias
from smashlib.ipy3x.core.completer import IPCompleter as IPCompleter


def complete_long_opts(cmd):
    """ completes long-opts args for any command,
        assuming it supports --help
    """
    tmp = subprocess.check_output(cmd + ' --help', shell=True)
    out = re.compile('\s+--[a-zA-Z]+').findall(tmp)
    out += re.compile('\s+-[a-zA-Z]+').findall(tmp)
    out = [x.strip() for x in out]
    out = list(set(out))
    return out


#FIXME: deprecated?
class opt_completer(object):
    """ """

    def __init__(self, cmd_name):
        self.cmd = cmd_name

    def __call__(self, fxn):
        def OptCompleter(himself, event):
            line = event.line
            if line and line.split()[-1].startswith('-'):
                return complete_long_opts(self.cmd)
            return fxn(himself, event)
        return OptCompleter


class SmashCompleter(IPCompleter):

    def asdasdcomplete(self, text, state):
        smash_log.debug("received data: [{0}]".format([text, state]))
        return super(SmashCompleter, self).complete(text, state)

    def magic_matches(self, text):
        # print 'Completer->magic_matches:',text,'lb',self.text_until_cursor # dbg
        # Get all shell magics now rather than statically, so magics loaded at
        # runtime show up too.
        lsm = self.shell.magics_manager.lsmagic()
        line_magics = lsm['line']
        cell_magics = lsm['cell']
        pre = self.magic_escape
        pre2 = pre + pre

        # Completion logic:
        # - user gives %%: only do cell magics
        # - user gives %: do both line and cell magics
        # - no prefix: do both
        # In other words, line magics are skipped if the user gives %%
        # explicitly
        bare_text = text.lstrip(pre)
        comp = [pre2 + m for m in cell_magics if m.startswith(bare_text)]
        if not text.startswith(pre2):
            comp += [pre + m for m in line_magics if m.startswith(bare_text)]
            # do not allow known shell commands to be prefixed
            # with '%' as if they were magic commands
            for i, x in enumerate(comp):
                original = x[len(pre):]
                if have_command_alias(original):
                    comp[i] = original
        return comp
