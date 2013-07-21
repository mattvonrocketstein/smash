""" smashlib.util.text_proc
"""
import re

def truncate_fpath(fpath):
    from smashlib.util import home
    return fpath.replace(home(), '~')

def split_on_unquoted_semicolons(txt):
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]
