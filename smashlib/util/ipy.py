""" smashlib.util.ipy

    import shortcuts for ipython.  this also might help to keep
    smashlib in sync with changing ipython target versions?
"""
import re
import keyword
from IPython.utils.coloransi import TermColors
from goulash.cache import MWT
from peak.util.imports import lazyModule
logging = lazyModule('smashlib._logging')

r_cmd = re.compile('^[\w-]+$')


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


@MWT(timeout=500)
def have_command_alias(x):
    """ this helper function is fairly expensive to be running on
        (almost) every input line.  caching seems tricky but necessary
    """
    if not r_cmd.match(x):
        return False
    blacklist = [
        # posix line oriented, not very useful so
        # this should not override ipython edit
        'ed',

        # often used as in ip=get_ipython()
        'ip',
    ] + keyword.kwlist
    if x in blacklist:
        result = False
    else:
        alias_list = get_ipython().alias_manager.aliases
        cmd_list = set()
        for alias, cmd in alias_list:
            if alias == cmd:
                cmd_list = cmd_list.union(set([alias]))
        result = x in cmd_list
    logging.smash_log.info('"{0}"? {1}'.format(x, result))
    return result
have_alias = have_command_alias


def register_prefilter(Checker, Handler):
    ip = get_ipython()
    pm = ip.prefilter_manager
    kargs = dict(
        shell=pm.shell,
        prefilter_manager=pm,
        config=pm.config)
    handler = Handler(**kargs)
    if Checker is not None:  # hack, remove with dotchecker exists
        checker = Checker(**kargs)
        ip.prefilter_manager.register_checker(checker)
    else:
        checker = None
    ip.prefilter_manager.register_handler(Handler.handler_name, handler, [])
    return checker, handler
