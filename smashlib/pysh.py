#!/usr/bin/env python
"""

"""
import re
import keyword
from IPython.core.prefilter import PrefilterHandler, Unicode, PrefilterChecker
from smashlib.python import ope

DOT_HANDLER_NAME   = 'DotHandler'
SHELL_HANDLER_NAME = 'ShellHandler'

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
        l0 = line_info.line[0]

        shandler = self.prefilter_manager.get_handler_by_name(SHELL_HANDLER_NAME)
        dhandler = self.prefilter_manager.get_handler_by_name(DOT_HANDLER_NAME)
        line = line_info.line
        split_line = line.split()
        if have_alias(split_line[0]):
            return shandler
        if l0 in '~/.':
            l1 = line[1]
            # if l1 is whitespace, this is probably some special syntax,
            # not something intended as instructions for the system shell
            # thus we will not mess with the input (perhaps the dot_prefilter
            # is interested in it.  see smashlib.dot_prefilter)
            if l0 == '.' and not ope(split_line[0]):
                return dhandler

from smashlib import get_smash
from smashlib.channels import C_DOT_CMD
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

class ShellHandler(PrefilterHandler):
    """ ShellHandler changes certain lines to system calls """
    handler_name = Unicode(SHELL_HANDLER_NAME)

    def handle(self, line_info):
        cmd = line_info.line.strip()
        return 'get_ipython().system(%r)' % (cmd, )


def have_command_alias(x):
    """ this helper function is fairly expensive to be running on
        (almost) every input line.  perhaps it should be cached, but

          a) answers would have to be kept in sync with rehashx calls
          b) the alias list must be getting checked all the time anyway?
    """
    blacklist = [
        'ed',    # posix line oriented, not as useful as ipython edit
        'ip',    # often used as in ip=get_ipython()
        ] + keyword.kwlist
    if x in blacklist:
        return False
    else:
        alias_list = get_ipython().alias_manager.aliases
        cmd_list = [ cmd for alias, cmd in alias_list ]
        return x in cmd_list
have_alias = have_command_alias

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    pm = ip.prefilter_manager
    kargs = dict(
        shell=pm.shell,
        prefilter_manager=pm,
        config=pm.config)
    checker = ShellChecker(**kargs)
    handler = ShellHandler(**kargs)
    ip.prefilter_manager.register_checker(checker)
    ip.prefilter_manager.register_handler(SHELL_HANDLER_NAME, handler, [])
    ip.prefilter_manager.register_handler(DOT_HANDLER_NAME, DotHandler(**kargs), [])
    return checker, handler


def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    # are singletons involved here?  not sure we can use
    # manager.unregister_handler() etc, since it does an
    # instance check instead of a class check.
    #
    # TODO: unload dothandler
    ip = get_ipython()
    handlers = ip.prefilter_manager.handlers
    for handler_name, handler in handlers.items():
        if isinstance(handler, ShellHandler):
            break
    del handlers[handler_name]
    checker_list = ip.prefilter_manager._checkers
    for tmp in checker_list:
        if isinstance(tmp, ShellChecker):
            del checker_list[checker_list.index(tmp)]
