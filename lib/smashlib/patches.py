""" smashlib.patches

    yup, this means I need to use IPython.ipmaker.make_IPython..
"""

import new
from smashlib.util import (report, report_if_verbose,
                           do_it_later, replace_magic)

# copied and modified from IPython.completer
def global_matches(self, text):
    """Compute matches when text is a simple name.

    Return a list of all keywords, built-in functions and names currently
    defined in self.namespace or self.global_namespace that match.

    """
    matches = []
    match_append = matches.append
    n = len(text)
    for lst in [#keyword.kwlist,
                #__builtin__.__dict__.keys(),
                self.namespace.keys(),
                self.global_namespace.keys()]:
        for word in lst:
            if word[:n] == text and word != "__builtins__":
                match_append(word)
    return matches

def replace_global_matcher():
    """ if this isn't done, then "ls <tab>" will show
        2 pages of junk, including python keywords and
        what not
    """
    do_it_later(lambda: setattr(__IPYTHON__.shell.Completer,
                                'global_matches',
                                new.instancemethod(global_matches,
                                                   __IPYTHON__.shell.Completer,
                                                   __IPYTHON__.shell.Completer.__class__)))

def replace_help_magic():
    """ patch that allows __qmark__(self) methods to answer "obj?" stlye
        requests from the command line interface.
    """
    original_pinfo = __IPYTHON__.shell.magic_pinfo
    def my_magic_pinfo(self, parameter_s='', namespaces=None):
        """ """
        call_original_pinfo = lambda: original_pinfo(parameter_s, namespaces)

        try:
            if parameter_s.startswith('%'):
                tmp = getattr(eval('__IPYTHON__.magic_'+parameter_s[1:]),
                              '__qmark__')
            else:
                tmp = getattr(eval(parameter_s, __IPYTHON__.user_ns), '__qmark__')
        except Exception,e: pass
        else:
            report_if_verbose.help_magic('found __qmark__!'+str(tmp))
            try:
                tmp()
            except Exception,e:
                raise
                #report.help_magic('__qmark__ defined but error encountered while calling it.')
                #report.help_magic('   :: '+str(e))
            return
        call_original_pinfo()
    report_if_verbose('replacing magic')
    replace_magic('magic_pinfo',
                  new.instancemethod(my_magic_pinfo,
                                     __IPYTHON__.shell,
                                     __IPYTHON__.shell.__class__))
