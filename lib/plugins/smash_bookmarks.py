"""
"""

from collections import defaultdict, namedtuple

import smashlib
from smashlib.projects import Project, COMMAND_NAME
from smashlib.util import report, ope, opj
from smashlib.plugins import SmashPlugin
from smashlib.aliases import RegistrationList

Bookmark = namedtuple('Bookmark', 'affiliation nickname uri'.split())

class Bookmarks(object):
    @property
    def _config_file(self):
        return opj(smashlib.SMASH_ETC_DIR, 'bookmarks.json')

    def _get_config(self, force=False):
        if not force and getattr(self,'_cached_config',None):
            return self._cached_config
        _file = self._config_file
        result = defaultdict(lambda:[])
        if ope(_file):
            dct = demjson.decode(open(_file).read())
            for k,v in dct.items(): result[k] = v
        return result
    def _set_config(self, config):
        _file = self._config_file
        with open(_file,'w') as fhandle:
            fhandle.write(demjson.encode(config))
        self._get_config(force=True)
    _config = property(_get_config, _set_config)

    @property
    def __doc__(self):
        """ niy """
        return str(self.groups)

    def ctx(self):
        out = ['__smash__']
        from smashlib import PROJECTS as proj
        out += [proj.CURRENT_PROJECT]
        return out

    @property
    def bookmarks(self):
        p = __IPYTHON__.user_ns[COMMAND_NAME]._active_project
        report.bm(str(p))


class Plugin(SmashPlugin):
    requires = []
    report = report.bookmark_plugin

    def install(self):
        if 'bookmarks' in __IPYTHON__.user_ns:
            self.report("bookmarks name already taken in shell namespace."
                        "  refusing to continue")
        else:
            __IPYTHON__.user_ns.update(bookmarks=Bookmarks())
