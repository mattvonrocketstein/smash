""" SmaSh plugin describing support and shortcuts
    for the duckduckgo search engine.

    TODO: 'requires' is not currently enforced
"""
import threading
from smashlib.util import report
from smashlib.smash_plugin import SmashPlugin

class Plugin(SmashPlugin):
    """ TODO: caching, integrate with bookmarks """

    requires = [ 'pynotify', 'duckduckgo' ]

    class q(object):
        """

        Simple operations:

           Excuting plain duckduckgo searches is asynchronous.

              q('multiple', 'words')
              q('multiple words')
              ,q singleWord

           execute "bang" search, aka "exclusive" aka site-search.
           if possible, these are opened in an existing webbrowser immediately.

              q.wiki('world war 2')
              ,q.wiki world war 2
              ,q.stacktrace python quicksort

        """

        def __getattr__(self, name):
            return lambda *x: self( *(('!'+name,) + x) )

        def note(self, msg):
            import pynotify
            pynotify.init("Test Capabilities")
            caps = pynotify.get_server_caps()
            note = pynotify.Notification('Search "{0}" finished'.format(self.last_search), msg)
            return note

        def __call__(self, *search_string):
            search_string = ' '.join(search_string)
            self.last_search = search_string
            def func():
                import webbrowser
                import duckduckgo
                result = duckduckgo.query(search_string)
                if result.type=='exclusive':
                    note = self.note("Opening {0}".format(result.redirect.url))
                    webbrowser.open_new_tab(result.redirect.url)
                else:
                    note   = self.note('type={0} related={1}'.format(result.type, len(result.related)))
                    note.set_timeout(120*1000) # dont auto-hide for two minutes
                    def callback(*args, **kargs):
                        print 'args/kargs', args, kargs
                        for r in result:
                            print r.text
                    note.add_action('show results', callback)
                note.show()
                __IPYTHON__.user_ns.update(result = result)
                return result, note

            threading.Thread(target=func).start()
    q = q()

    def install(self):
        self.contribute('q', self.q)
        """
        if 'q' in __IPYTHON__.user_ns:
            report.quacker('"q" variable is taken in user namespace.  refusing to proceed')
        else:
            #self.q.stackoverflow = lambda *search_string: self.q('!stackoverflow',*search_string)
            __IPYTHON__.user_ns.update(q=self.q)
            report.quacker("finished installing.  type 'q?' for help with search")
            """
