"""
"""
import smashlib
from smashlib.util import report, ope, opj, set_complete
from smashlib.plugins import SmashPlugin

def pydict_completer(self,event):
    dotpath_before_dict = event.line[:event.line.find('[')]
    try:
        result = eval(dotpath_before_dict, __IPYTHON__.user_ns)
    except Exception,e:
        report.dictionary_completion('error:' + str(e))
    else:
        result=[k+"]" for k in result.keys()]
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        return result
        #return result.keys()

def pydict_completer2(self, event):
    # this is various ipython stuff that's cluttering the namespace
    FORBIDDEN  = 'os sout pysh In Out lout help getoutput getoutputerror shell system'.split()
    FORBIDDEN += 'proj plugins bookmarks q recentf'.split()
    base = [ x for x in __IPYTHON__.user_ns.keys() if not x.startswith('_') ]
    base = [ x for x in base if x not in FORBIDDEN ]
    return [ x for x in pydict_completer(self, event) ] + base


class Plugin(SmashPlugin):
    requires = []
    report = report.bookmark_plugin

    def install(self):
        set_complete(pydict_completer, '''.*\[[\'\"]''')
        set_complete(pydict_completer2, '''.*\[$''')
