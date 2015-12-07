""" smashlib.prefilters.shell
"""
import re
from smashlib._logging import smash_log
from smashlib.util.ipy import have_alias

from IPython.core.prefilter import PrefilterHandler, Unicode, PrefilterChecker

#from smashlib._logger import smash_log
HANDLER_NAME = 'ShellHandler'

#initial_assignments = re.compile(r'^\s*(((\w+=\w+ )|(\w+=\"\w*\" ))+) ', flags=re.MULTILINE)
initial_assignments = re.compile(r'^\s*(((\w+=\w+ ))|(\w+=\".*\" ))+', flags=re.MULTILINE)
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
        prefixed_assignments = initial_assignments.search(line)
        if prefixed_assignments:
            smash_log.info('detected prefixed assignments')
            only_assignments = prefixed_assignments.group()
            nonassignment_section = line[len(only_assignments):]
            maybe_command = nonassignment_section.split()
            maybe_command = maybe_command and maybe_command[0]
            if have_alias(maybe_command):
                smash_log.info('prefixed assignments are followed by command alias')
                return shandler
        split_line = line.split()
        if have_alias(split_line[0]):
            return shandler
