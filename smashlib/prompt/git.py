""" smashlib.prompt.git
"""

from goulash._fabric import qlocal

def current_branch():
    result = qlocal('''git branch|grep \*''', capture=True).strip().split()
    result = result[-1] if result else ''
    return result
