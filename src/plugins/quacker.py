""" quacker:

     SmaSh support for duckduckgo search engine
"""

from smash.util import report
from smash.plugins import SmashPlugin


#if caps and 'actions' in caps:
    # We support actions, so add a button.
#notification.add_action("ignore", "Ignore", ignore_cb)

class QuackerPlugin(SmashPlugin):
    """ TODO: caching, integrate with bookmarks """

    requires = [ 'duckduckgo' ]

    class q(object):

        def __getattr__(self, name):
            return lambda *x: self( *(('!'+name,) + x) )

        def note(self, msg):
            import pynotify
            pynotify.init("Test Capabilities")
            caps = pynotify.get_server_caps()
            note = pynotify.Notification('Search "{0}" finished'.format(self.last_search), msg)
            return note

        def __call__(self, *search_string):
            """
            q('querystring')       excute plain duckduckgo search
            q.wiki('querystring')  excute duckduck "exclusive" aka bang aka site-search
            """
            search_string = ' '.join(search_string)
            self.last_search = search_string
            def func():
                import webbrowser
                import duckduckgo
                result = duckduckgo.query(search_string)
                note   = self.note('type={0} related={1}'.format(result.type, len(result.related)))
                if result.type=='exclusive':
                    webbrowser.open_new_tab(result.redirect.url)
                    note.show()
                else:
                    note.set_timeout(120*1000) # dont auto-hide for two minutes
                    def callback(*args, **kargs):
                        print 'args/kargs', args, kargs
                        for r in result:
                            print r.text
                    note.add_action('show results', callback)
                    note.show()
                __IPYTHON__.user_ns.update(result=result)
                return result,note
            import threading
            threading.Thread(target=func).start()
            #return func()
    q = q()

    def install(self):
        if 'q' in __IPYTHON__.user_ns:
            report.quacker('"q" variable is taken in user namespace.  refusing to proceed')
        else:
            #self.q.stackoverflow = lambda *search_string: self.q('!stackoverflow',*search_string)
            __IPYTHON__.user_ns.update(q=self.q)
            report.quacker("finished installing.  type 'q?' for help with search")

def smash_install():
    QuackerPlugin().install()
