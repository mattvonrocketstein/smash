""" plugins/smash_misc_python
"""

import os, glob
from types import ModuleType

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import (\
    post_hook_for_magic, truncate_fpath,
    report, report_if_verbose, _ip, set_complete)
from smashlib.python import opj, opd
from smashlib.reflect import namedAny, ModuleNotFound, ObjectNotFound


class PyToPackage(object):
    def __qmark__(self):
        report.py2package("converts an individual .py file "
                          "(or python dotpath) into a package.")

    def report(self, *args, **kargs):
        report.py2package(*args, **kargs)

    def __call__(self, str_arg):
        self.report('assuming dotpath..')
        try:
            arg = namedAny(str_arg)
        except (ModuleNotFound, ObjectNotFound):
            self.report('not a dotpath.  hope this is a file.')
            arg = str_arg
        else:
            if arg:
                self.report('resolved dotpath')
                if not isinstance(arg, ModuleType):
                    _ = 'imported from dotpath, but got {0} instead of moduletype'
                    self.report(_.format(type(arg)))
                    return
                else:
                    self.report("result is module.. good")
                    arg = arg.__file__

        arg = os.path.abspath(arg)
        if not ope(arg):
            self.report('no such file: '+arg)
        else:
            self.report('chose file: {0}'.format(arg))
            new_dirname,ext = os.path.splitext(arg)
            if ext!='.py':
                self.report('this is not a python file.. aborting')
                return
            if ope(new_dirname):
                self.report('aborting, dirname@{0} already exists.'.format(new_dirname))
                return
            self.report('making directory@"{0}"'.format(new_dirname))
            try:
                os.mkdir(new_dirname)
            except OSError,e:
                self.report('error: {0}'.format(new_dirname,str(e)))
                return
            src,dst = arg, opj(new_dirname,'__init__.py')
            self.report('moving "{0}" --> "{1}"'.format(src, dst))
            try:
                shutil.move(src, dst)
            except IOError,e:
                self.report('error: {0}'.format(new_dirname,str(e)))

class SearchSite(object):
    def __qmark__(self):
        report.search_site("based on your environment I will look here:")
        report.search_site("  " + truncate_fpath(self.lib_py))

    @property
    def lib_py(self):
        return opj(
            os.environ['VIRTUAL_ENV'],'lib',
            'python*','site-packages')

    def __call__(self, query):
        lib_py = self.lib_py
        # globbing because there is potentially
        # one dir for 2.6, one for 2.7, etc etc
        lib_py = glob.glob(lib_py)
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

    requires = ['which']

    def install(self):
        self.contribute_magic('search_site', SearchSite())
        self.contribute_magic('py2package', PyToPackage())
