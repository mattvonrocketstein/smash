""" smashlib.prompt
"""
import os

from goulash._fabric import qlocal
from goulash._os import get_term_size
MAX_LENGTH = 25


def div():
    lines, cols = get_term_size()
    return '-' * cols


def user_symbol():
    if os.environ.get('USER') != 'root':
        return '$'
    else:
        return '#'


def working_dir():
    wd = os.getcwd()
    home = os.environ.get('HOME')
    under_home = home and home in wd
    if under_home:
        wd = wd.replace(home, '~')
    return wd


def git_branch():
    result = qlocal('''git branch|grep \*''', capture=True).strip().split()
    result = result[-1] if result else ''
    return result


def venv():
    result = os.environ.get('VIRTUAL_ENV', '')
    if result:
        result = os.path.split(result)[-1]
    return result
