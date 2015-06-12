""" smashlib.prefilters.shell
"""

from smashlib.util.ipy import have_alias

from IPython.core.prefilter import PrefilterHandler, Unicode, PrefilterChecker

#from smashlib._logger import smash_log
HANDLER_NAME = 'ShellHandler'

class ShellHandler(PrefilterHandler):
    """ ShellHandler changes certain lines to system calls """
    handler_name = Unicode(HANDLER_NAME)

    def handle(self, line_info):
        cmd = line_info.line.strip()
        #smash_log.info("shellhandler: {0}".format(cmd))
        return 'get_ipython().system(%r)' % (cmd, )

class ShellChecker(PrefilterChecker):
    """ shell checker should really run before anything else """

    priority = 50

    def check(self, line_info):
        """ note: the way that line_info splitting happens means
            that for a command like "apt-get foo", first/rest will
            be apt/-get foo.  it's better to just use line_info.line
        """
        if line_info.continue_prompt or not line_info.line.strip():
            return None
        shandler = self.prefilter_manager.get_handler_by_name(HANDLER_NAME)
        line = line_info.line
        split_line = line.split()
        if have_alias(split_line[0]):
            return shandler
