""" smashlib.util.bash
    see also: smashlib.bin.pybcompgen
"""

import re
from subprocess import Popen, PIPE

from smashlib.bin.pybcompgen import remove_control_characters

r_alias=re.compile('alias \w+=.*')

def get_aliases():
    cmd = 'bash -c "echo alias|bash -i"'
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    lines = out.split('\n')
    lines = [x for x in lines if r_alias.match(x)]
    aliases=[]
    for line in lines:
        line = ' '.join(line.split()[1:]) # first word is 'alias'
        equals_sign = line.find('=')
        alias = line[:equals_sign]
        cmd = line[equals_sign+1:].strip()
        cmd=remove_control_characters(unicode(cmd))
        #cmd may or may not be quoted
        cmd = cmd[1:-1] if cmd[0] in ['"',"'"] else cmd
        aliases.append([alias,cmd])
    return aliases

def get_functions():
    cmd = '''bash -c "echo 'echo MARKER;compgen -A function;echo MARKER'|bash -i"'''
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    lines = out.split('\n')
    lines = [ x.strip() for x in lines ]
    lines = [ x for x in lines if x and not x.startswith('_') ]
    lines = [ x for x in lines if re.compile('\w*').match(x)]
    lines = lines[lines.index('MARKER')+1:]
    lines = lines[:lines.index('MARKER')]
    function_names = lines
    return function_names

from report import report
def bash_function(fxn_name, input_string, quiet=False):
    """ if you have quoted values in input_string, this will probably break"""
    report("Running: {0} {1}".format(fxn_name, input_string))
    cmd = '''bash -c "echo 'echo MARKER;{0} {1};echo MARKER'|bash -i"'''
    cmd = cmd.format(fxn_name, input_string)
    p1 = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    lines = out.split('\n')
    lines = [ x.strip() for x in lines ]
    lines = lines[lines.index('MARKER')+1:]
    lines = lines[:lines.index('MARKER')]
    if not quiet:
        print '\n'.join(lines)
    return lines

if __name__=='__main__':
    #get_aliases()
    print get_functions()
    print bash_function('checkport', '8080')
