""" smashlib.util.bash
    see also: smashlib.bin.pybcompgen
"""

import re
import unicodedata
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

if __name__=='__main__':
    get_aliases()
