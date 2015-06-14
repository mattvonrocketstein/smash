""" smashlib.prompt.OS
"""

import os
from goulash._fabric import qlocal

def user_symbol():
    if os.environ.get('USER')!='root':
        return '$'
    else:
        return '#'
