""" smashlib.pysh
"""
from smashlib.util.ipy import register_prefilter
from smashlib.prefilters.shell import ShellHandler, ShellChecker


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    checker, handler = register_prefilter(ShellChecker, ShellHandler)
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
