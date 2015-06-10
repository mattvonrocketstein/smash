""" smashlib.plugins.summarize

    documentation: http://mattvonrocketstein.github.io/smash/plugins.html#summarize
"""

import os
from report import console

from goulash.python import ope
from goulash.venv import find_venvs
from goulash._fabric import require_bin

from smashlib.plugins import Plugin
from smashlib.util import guess_dir_type


def sloccount(_dir):
    require_bin('sloccount')
    cmd_t = 'sloccount "{0}"'.format(_dir)
    lines = os.popen(cmd_t).readlines()
    # cut off information about how to cite the tool
    tmp = ''.join(lines[:-6])
    # cut off preamble
    tmp = tmp.split('Computing results.\n')[1:][0]
    tmp = [x for x in tmp.split('\n\n') if x]
    # strip leading newline from each section
    tmp = [ (x if not x.startswith('\n') else x[1:]) for x in tmp ]
    one,two,three = tmp
    one = [x for x in one.split('\n') if x[0]!='0']
    one= '\n'.join(one)
    tmp = [x.strip() for x in [three, one, two,]]
    return tmp

def summarize(parameter_s=''):
    _dir = parameter_s or os.getcwd()
    assert ope(_dir)
    tmp = guess_dir_type(_dir)
    print console.red('match types:')
    console.draw_line()
    print ' {0}'.format(tmp)
    print console.red('virttualenvs:')
    console.draw_line()
    print ' {0}'.format(find_venvs(_dir))
    print console.red('sloccount:')
    for report_section in sloccount(_dir):
        console.draw_line()
        print report_section.strip()
    console.draw_line()

class Summarize(Plugin):
    def init(self):
        self.contribute_magic(summarize)
        #self.contribute_magic(sloccount)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return Summarize(get_ipython()).install()

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'
