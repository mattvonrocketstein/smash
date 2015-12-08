# -*- coding: utf-8 -*-
""" smashlib.prompt
"""
import os

from IPython.utils.coloransi import TermColors
from goulash._fabric import qlocal
from goulash._os import get_term_size
MAX_LENGTH = 25
from smashlib.bin.pybcompgen import remove_control_characters

def div():
    lines, cols = get_term_size()
    return '-' * cols


def user_symbol():
    if os.environ.get('USER') != 'root':
        return '$'
    else:
        return '#'

def is_ssh():
    _vars = "SSH_CLIENT SSH2_CLIENT SSH_TTY"
    for v in _vars.split():
        if os.environ.get(v):
            return True
#def host
#https://stackoverflow.com/questions/1616678/bash-pwd-shortening
def abbreviated_working_dir(length=10):
    """ """
    ellipsis = '..' #TermColors.DarkGray+".."+TermColors.Normal
    path = unexpand(os.getcwd())
    while len(remove_control_characters(path)) > length:
        dirs = path.split(os.path.sep);

        # Find the longest directory in the path.
        max_index  = -1
        max_length = 4

        for i in range(len(dirs) - 1):
            if len(dirs[i]) > max_length:
                max_index  = i
                max_length = len(dirs[i])

        # Shorten it by one character.
        if max_index >= 0:
            dirs[max_index] = dirs[max_index][:max_length-3] + ellipsis
            path = "/".join(dirs)

        # Didn't find anything to shorten. This is as good as it gets.
        else:
            break
    return path

def unexpand(path):
    """ opposite of os.path.expanduser """
    home = os.environ.get('HOME')
    under_home = home and home in path
    if under_home:
        path = path.replace(home, '~')
    return path

def working_dir():
    wd = os.getcwd()
    return unexpand(wd)


def git_branch():
    result = qlocal('''git branch|grep \*''', capture=True).strip().split()
    result = result[-1] if result else ''
    changes=qlocal('git ls-files -m', capture=True).strip()
    if changes:
        return '{color.Red}' + result + '{color.Normal}'
    else:
        return '{color.Green}' + result + '{color.Normal}'
    return result


def venv():
    result = os.environ.get('VIRTUAL_ENV', '')
    if result:
        result = os.path.split(result)[-1]
    return result
