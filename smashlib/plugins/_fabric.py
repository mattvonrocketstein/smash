""" smashlib.plugins.fabric
    documentation: http://mattvonrocketstein.github.io/smash/plugins.html#fabric
"""
import ast

from smashlib.plugins import Plugin
from goulash.python import ope
from smashlib.completion import opt_completer
from smashlib._logging import smash_log, completion_log

fabric_opt_completer = opt_completer('fab')


def fabric_cmd_completer(self, event):
    smash_log.info('event [{0}]'.format(event.__dict__))
    if event.symbol.startswith('-'):
        return []
    if ope('fabfile.py'):
        _fabfile = 'fabfile.py'
    elif ope('Fabfile.py'):
        _fabfile = 'Fabfile.py'
    else:
        smash_log.info("no fabfile was found")
        return []
    with open(_fabfile, 'r') as fhandle:
        src = fhandle.read()
    node = ast.parse(src)
    return list([x.name for x in ast.walk(node) if
                 isinstance(x, ast.FunctionDef)])


class FabricPlugin(Plugin):

    def init(self):
        completion_log.info("adding fabric completer")
        self.smash.add_completer(fabric_cmd_completer, re_key='fab')
        self.smash.add_completer(fabric_opt_completer, re_key='fab -')
        self.smash.add_completer(fabric_opt_completer, re_key='fab --')
        return self


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return FabricPlugin(get_ipython()).install()
