""" smashlib.util.ipy

    import shortcuts for ipython.  this also might help to keep
    smashlib in sync with changing ipython target versions?
"""
from IPython.utils.coloransi import TermColors

def green(txt):
    return TermColors.Green + txt + TermColors.Normal
