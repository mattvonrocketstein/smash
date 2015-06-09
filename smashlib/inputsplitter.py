""" smashlib.inputsplitter
"""

import re
from goulash.python import ope

from IPython.core.inputsplitter import IPythonInputSplitter

r_ed = 'ed [^:]*'

class SmashInputSplitter(IPythonInputSplitter):
    """ It may be useful for something else in the future, but at the moment
        Smash overrides the core IPythonInputSplitter for just one reason:

        We want to force commands like "ed /some/path/file_name.txt:<col>:"
        to be interpretted as complete input.  The use case is that simply that
        this format is often used as output for command line tools (for
        instance ack-grep)
    """
    def push(self, lines):
        result = super(SmashInputSplitter, self).push(lines)
        lines = lines.strip()
        match = re.compile(r_ed).match(lines)
        if match:
            fname = match.group().split()[1]
            if ope(fname):
                self.source += '\n'
        return result
