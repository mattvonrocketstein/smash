""" smashlib.prefilters.url
"""

import urlparse
from IPython.core.prefilter import PrefilterHandler, Unicode, PrefilterChecker

from smashlib import get_smash
from smashlib.channels import C_URL_INPUT

HANDLER_NAME   = 'URLHandler'
PROTOS = 'http https ssh ftp'.split()


class URLHandler(PrefilterHandler):

    handler_name = Unicode("URLHandler")

    def handle(self, line_info):
        """ when the dot handler is engaged, we send a signal
            and then prefilter the input to empty-string, which is
            effectively a no-op.  anyone that wants to act on the
            dot-cmd can receive the signal.
        """
        line = line_info.line.strip()
        get_smash().publish(C_URL_INPUT, line, urlparse.urlparse(line_info.line))
        return ""

class URLChecker(PrefilterChecker):
    """ url checker should run before most other checkers! """

    priority = 1

    def check(self, line_info):
        def get_scheme(clean_line):
            scheme = urlparse.urlparse(clean_line).scheme
            if scheme in PROTOS:
                return scheme
        scheme = get_scheme(line_info.line.strip())
        if scheme is not None:
            dhandler = self.prefilter_manager.get_handler_by_name(HANDLER_NAME)
            return dhandler
