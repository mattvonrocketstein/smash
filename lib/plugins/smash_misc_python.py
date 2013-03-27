""" smash_misc_python
"""

import os
import smashlib
import glob
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import post_hook_for_magic
from smashlib.util import report, report_if_verbose, _ip, set_complete

def search_site(query):
    """ searches site projects for the currently-activated virtualenv
    """
    lib_py = opj(os.environ['VIRTUAL_ENV'],'lib','python*','site-packages')
    lib_py = glob.glob(lib_py) # potentially one dir for 2.6, one for 2.7, etc
    report.misc_python('searching: ' + str(lib_py))
    if '|' in query:
        parts = [x.strip() for x in query.split('|')]
        query = parts[0]
        filters = parts[1:] if len(parts)>1 else []
    else:
        filters = []
    for _dir in lib_py:
        line = 'ack "{0}" "{1}"'.format(query, _dir)
        for _filter in filters:
            tmp     = '"{0}"'.format(_filter)
            prepend = '' if _filter.startswith('grep') else ' grep'
            tmp     = '|'  + prepend + tmp
        report.misc_python('{red} ==> {normal}' + line)
        __IPYTHON__.system(line)

class Plugin(SmashPlugin):
    requires = ['ack']

    def install(self):
        self.contribute_magic('search_site', search_site)
