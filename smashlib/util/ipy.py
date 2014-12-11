""" smashlib.util.ipy

    import shortcuts for ipython.  this also might help to keep
    smashlib in sync with changing ipython target versions?
"""
import keyword
from IPython.utils.coloransi import TermColors

def green(txt):
    return TermColors.Green + txt + TermColors.Normal

def uninstall_prefilter(HandlerOrCheckerClass):
    """ uninstalls argument from running IPython instance,
        where the argument may be either a class describing either
        a prefilter Handler or a Checker.
    """
    # are singletons involved here?  not sure we can use
    # manager.unregister_handler() etc, since it does an
    # instance check instead of a class check.
    ip = get_ipython()
    # uninstall if handler
    handlers = ip.prefilter_manager.handlers
    for handler_name, handler in handlers.items():
        if isinstance(handler, HandlerOrCheckerClass):
            break
    del handlers[handler_name]
    # uninstall if checker
    checker_list = ip.prefilter_manager._checkers
    for tmp in checker_list:
        if isinstance(tmp, HandlerOrCheckerClass):
            del checker_list[checker_list.index(tmp)]

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

def register_prefilter(Checker, Handler):
    ip = get_ipython()
    pm = ip.prefilter_manager
    kargs = dict(
        shell=pm.shell,
        prefilter_manager=pm,
        config=pm.config)
    handler = Handler(**kargs)
    if Checker is not None:#hack, remove with dotchecker exists
        checker = Checker(**kargs)
        ip.prefilter_manager.register_checker(checker)
    else:
        checker=None
    ip.prefilter_manager.register_handler(Handler.handler_name, handler, [])
    return checker, handler
