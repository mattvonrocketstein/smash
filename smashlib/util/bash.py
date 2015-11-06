""" smashlib.util.bash
    see also: smashlib.bin.pybcompgen
"""

import re
from subprocess import Popen, PIPE

from report import console
from tabulate import tabulate

from smashlib.bin.pybcompgen import remove_control_characters
from smashlib._logging import smash_log

r_alias = re.compile('alias \w+=.*')


def get_aliases():
    """ extract all aliases from the underlying bash shell. """
    cmd = 'bash -c "echo alias|bash -i"'
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    lines = out.split('\n')
    lines = [x for x in lines if r_alias.match(x)]
    aliases = []
    for line in lines:
        line = ' '.join(line.split()[1:])  # first word is 'alias'
        equals_sign = line.find('=')
        alias = line[:equals_sign]
        cmd = line[equals_sign + 1:].strip()
        cmd = remove_control_characters(unicode(cmd))
        # cmd may or may not be quoted
        cmd = cmd[1:-1] if cmd[0] in ['"', "'"] else cmd
        aliases.append([alias, cmd])
    return aliases


def get_functions():
    """ extracts the names of all functions from the underlying bash shell """
    cmd = '''bash -c "echo 'echo MARKER1;compgen -A function|grep -v ^_.*;echo MARKER2'|bash -i"'''
    return _get_functions(cmd)

def _get_functions(cmd):
    """ """
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    lines = out.split('\n')
    lines = [x.strip() for x in lines]
    #lines = [x for x in lines if x and not x.startswith('_')]
    olines = [x for x in lines if re.compile('\w*').match(x)]
    #try:
    #raise Exception,cmd
    lines = olines[olines.index('MARKER1') + 1:]
    lines = lines[:lines.index('MARKER2')]
    #except ValueError:

    function_names = lines
    return function_names

def get_functions_from_file(fname):
    """ """
    base_functions = get_functions()
    cmd = '''bash -c "echo 'source '''+fname+''';echo MARKER1;compgen -A function|grep -v ^_.*;echo MARKER2'|bash -i"'''
    new_functions = _get_functions(cmd)
    return list(set(new_functions)-set(base_functions))

def run_function_in_host_shell(fxn_name, input_string, quiet=False):
    """ if you have quoted values in input_string, this will probably break"""
    if not quiet:
        report("Running: {0} {1}".format(fxn_name, input_string))
    cmd = '''bash -c "echo 'echo MARKER;{0} {1};echo MARKER'|bash -i"'''
    cmd = cmd.format(fxn_name, input_string)
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    lines = out.split('\n')
    lines = [x.strip() for x in lines]
    lines = lines[lines.index('MARKER') + 1:]
    lines = lines[:lines.index('MARKER')]
    if not quiet:
        print '\n'.join(lines)
    return lines


class FunctionMagic(object):
    """ call bridge connecting smash to a bash function """

    def __init__(self, fxn_name, source='??'):
        self.name = fxn_name
        self.last_result = None
        self.source = source

    def __qmark__(self):
        """ user-friendly information when the input is "<bash_fxn>?" """
        name, source = map(str, [self.name, self.source])
        table = [
            ['type:','bash function'],
            ['source:', str(source)],
            ['source name:',name],
            ['smash name:', name],
            ]

        table = tabulate(table) #string from list
        table = table.split('\n')[1:-1] # back to list (removing header/footer)
        table = [ console.blue('  | ') + x for x in table ]
        out = out = [ console.red('Smash-Bash bridge:') ] + table
        return '\n'.join(out)

    def __call__(self, parameter_s):
        self.last_result = run_function_in_host_shell(self.name, parameter_s)
