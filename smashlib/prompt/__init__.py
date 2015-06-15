""" smashlib.prompt
"""
import os
from goulash._fabric import qlocal

def user_symbol():
    if os.environ.get('USER')!='root':
        return '$'
    else:
        return '#'

def git_branch():
    result = qlocal('''git branch|grep \*''', capture=True).strip().split()
    result = result[-1] if result else ''
    return result

def venv():
    result = os.environ.get('VIRTUAL_ENV','')
    if result:
        result = os.path.split(result)[-1]
    return result
