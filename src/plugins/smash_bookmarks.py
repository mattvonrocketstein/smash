"""
"""

from smash.projects import Project, COMMAND_NAME
from smash.util import report
from smash.plugins import SmashPlugin

class Bookmarks(object):
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
