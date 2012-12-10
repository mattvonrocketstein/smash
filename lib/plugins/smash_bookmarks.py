""" bookmarks
"""
from __future__ import print_function
import webbrowser

from collections import defaultdict, namedtuple

import smashlib
from smashlib.projects import Project
from smashlib.util import report, ope, opj, list2table
from smashlib.util import add_shutdown_hook, post_hook_for_magic
from smashlib.plugins import SmashPlugin
from smashlib.aliases import RegistrationList

class Bookmark(namedtuple('Bookmark', 'affiliation nickname uri'.split())):
    def launch(self):
        webbrowser.open_new_tab(self.uri)

class BookmarkLauncher(property):
    pass

class Bookmarks(object):
    CMD_NAME = 'bookmarks'

    def __iter__(self):
        for group in self._config.keys():
            entries = self._config[group]
            for entry in entries:
                entry    = entry.split()
                nickname = entry[0]
                rest     = ' '.join(entry[1:])
                yield Bookmark(affiliation=group,
                               nickname=nickname,
                               uri=rest)
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
        with open(_file, 'w') as fhandle:
            fhandle.write(demjson.encode(config))
        self._get_config(force=True)
    _config = property(_get_config, _set_config)

    @property
    def __doc__(self):
        out = ('Note that this only shows bookmarks which are relevant for the '
               'current context.  If you want to see all bookmarks, '
               'type "bookmarks.everything?"'
               '\n\nBookmarks:\n{0}')
        dat, headers = self._doc_helper(self._relevant_context())
        out = out.format(list2table(dat, header=headers))
        return out
        #out = out.format(list2table(dat, header=headers))
        #dat, headers = doit(self._relevant_context())

    def _doc_helper(self, keys):
        """ get a table for some subset of the bookmarks """
        dat = []
        for bookmark in self:
            if bookmark.affiliation in keys:
                dat.append([bookmark.affiliation,
                            bookmark.nickname, bookmark.uri])
        headers='group nickname pointer'.split()
        return dat, headers

    def _relevant_context(self):
        """ returns a list of all the bookmark subgroups
            that are  relevant to the current context.
        """
        out = ['__smash__']
        from smashlib import PROJECTS as proj
        out += [ proj.CURRENT_PROJECT ]
        return out

    def _maybe_update(self):
        count = 0
        relevant_groups = self._relevant_context()
        for x in dir(self):
            obj = getattr(self, x)
            if isinstance(obj, BookmarkLauncher):
                delattr(self.__class__,
                        x)
                count+=1
        if count:
            msg = 'removed {0} stale bookmarks from the context'
            msg = msg.format(count)
            report.bookmarks(msg)

        z = [ [x.nickname, lambda p: report(x.uri) ] for x in self ]
        #if x.affiliation in relevant_groups:
        for q in z:
            setattr(self.__class__,
                    q[0],
                    BookmarkLauncher(q[1]))


class Plugin(SmashPlugin):
    requires = []
    report = report.bookmark_plugin

    def install(self):
        if 'bookmarks' in __IPYTHON__.user_ns:
            self.report("bookmarks name already taken in shell namespace."
                        "  refusing to continue")
        else:
            bookmarks = Bookmarks()
            import smashlib
            smashlib.BOOKMARKS = bookmarks
            self.contribute('bookmarks', bookmarks)
            post_hook_for_magic('cd', bookmarks._maybe_update)
            #post_hook_for_activation(bookmarks._maybe_update)
