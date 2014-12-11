""" smashlib.prefilters.dot
"""

from IPython.core.prefilter import PrefilterHandler, Unicode, PrefilterChecker

from smashlib import get_smash
from smashlib.channels import C_DOT_CMD
from goulash.python import ope

DOT_HANDLER_NAME   = 'DotHandler'

class DotHandler(PrefilterHandler):

    handler_name = Unicode("DotHandler")

    def handle(self, line_info):
        """ when the dot handler is engaged, we send a signal
            and then prefilter the input to empty-string, which is
            effectively a no-op.  anyone that wants to act on the
            dot-cmd can receive the signal.
        """
        line = line_info.line.strip()[1:]
        get_smash().publish(C_DOT_CMD, line)
        return ""

class DotChecker(PrefilterChecker):
    """ shell checker should run before most other checkers! """

    priority = 50

    def check(self, line_info):
        """ note: the way that line_info splitting happens means
            that for a command like "apt-get foo", first/rest will
            be apt/-get foo.  it's better to just use line_info.line
        """
        if line_info.continue_prompt or not line_info.line.strip():
            return None
        l0 = line_info.line[0]
        dhandler = self.prefilter_manager.get_handler_by_name(DOT_HANDLER_NAME)
        split_line = line_info.line.split()
        if l0 in '~/.':
            #l1 = line[1]
            # if l1 is whitespace, this is probably some special syntax,
            # not something intended as instructions for the system shell
            # thus we will not mess with the input (perhaps the dot_prefilter
            # is interested in it.  see smashlib.dot_prefilter)
            if l0 == '.' and not ope(split_line[0]):
                return dhandler
