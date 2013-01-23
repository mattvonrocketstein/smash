""" smash_bookmarks:

      a plugin adding support for http/ssh/file-style bookmarks
"""
import webbrowser
from collections import defaultdict, namedtuple

import smashlib
from smashlib.projects import Project
from smashlib.util import bus
from smashlib.util import report, ope, opj, list2table,colorize
from smashlib.util import add_shutdown_hook, post_hook_for_magic
from smashlib.smash_plugin import SmashPlugin
from smashlib.aliases import RegistrationList

def bookmarks_cmp(x,y):
    """ utility for sorting based on group, then nickname """
    l1 = cmp(x.affiliation, y.affiliation)
    return cmp(x.nickname, y.nickname) if l1==0 else l1

class Bookmark(namedtuple('Bookmark', 'affiliation nickname uri'.split())):
    def launch(self):
        import urlparse, os
        parsed = urlparse.urlparse(self.uri)
        if parsed.scheme=='ssh':
            netloc = parsed.netloc
            if '@' not in netloc:
                netloc = os.environ['USER']+'@' + netloc
            user, host=netloc.split('@')
            cmd_t = 'ssh -l {user} {host}'
            cmd = cmd_t.format(user=user, host=host)
            report.executing(cmd)
            return __IPYTHON__.system(cmd)
        elif parsed.scheme in 'http https ftp file'.split():
            return webbrowser.open_new_tab(self.uri)
        else:
            report('dont know how to work with {0} scheme yet'.format(parsed.scheme))

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
        out = colorize(
            '\n{red}Hints:{normal} (try typing these)\n'
            '  bookmarks[index]         launches the bookmark at `index`\n'
            '  bookmarks[nickname]      launches the bookmark named `nickname`\n'
            '  bookmarks.everything?    shows all the bookmarks\n'
            '  bookmarks.files?         shows all file bookmarks\n'
            '  bookmarks.ssh?           shows all ssh bookmarks\n'
            '\n\n{red}Bookmarks for this context:{normal}\n\n')
        try:
            dat, headers = self._doc_helper(self._relevant_context())
            tmp = list2table(dat, header=headers, indent='  ')
        except Exception,e:
            return "Error building bookmark summary: "+str(e)
        else:
            return out+tmp

    def _sorted_bookmarks(self, keys):
        bookmarks = [b for b in self if b.affiliation in keys]
        bookmarks.sort(bookmarks_cmp)
        return bookmarks

    def _relevant_bookmarks(self):
        return self._sorted_bookmarks(self._relevant_context())

    def __getitem__(self, index_or_name):
        context = self._relevant_bookmarks()
        error = lambda: report("no such bookmark.  type {red}bookmarks?{normal} for help")
        try:
            return context[index_or_name].launch()
        except TypeError:
            choice = [ bookmark for bookmark in context if bookmark.nickname==index_or_name ]
            if not choice: return error()
            elif len(choice)>1:
                report('multiple bookmarks match that name.  check your configuration')
            else:
                choice = choice[0]
                choice.launch()
        except IndexError:
            error()


    def _doc_helper(self, keys):
        """ get a table for some subset of the bookmarks """
        dat = []
        bookmarks = self._sorted_bookmarks(keys)
        for bookmark in bookmarks:
            index = bookmarks.index(bookmark)
            dat.append([index,
                        bookmark.affiliation,
                        bookmark.nickname, bookmark.uri])
        headers='index group nickname uri'.split()
        return dat, headers

    def _relevant_context(self):
        """ returns a list of all the bookmark subgroups
            that are  relevant to the current context.
        """
        out = ['__smash__']
        from smashlib import PROJECTS as proj
        out += [ proj.CURRENT_PROJECT ]
        return out

    def _maybe_update(self, *args, **kargs):
        """ proof of concept.. """
        report('updating bookmarks ' + str(kargs))
        return

class Plugin(SmashPlugin):
    requires = []
    report = report.bookmark_plugin

    def install(self):
        if 'bookmarks' in __IPYTHON__.user_ns:
            self.report("bookmarks name already taken in shell namespace."
                        "  refusing to continue")
        else:
            bookmarks = Bookmarks()
            self.contribute('bookmarks', bookmarks)
            post_hook_for_magic('cd', bookmarks._maybe_update)

            bus().subscribe('post_activate', bookmarks._maybe_update)
