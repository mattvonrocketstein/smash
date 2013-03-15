""" smashlib.patches

    yup, this means I need to use IPython.ipmaker.make_IPython..
"""

import new

from smashlib.util import do_it_later

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
