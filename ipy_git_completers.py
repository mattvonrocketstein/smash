""" ipy_git_completers

    TODO: subcommands 'mv' and 'add' should use file-system completion
    TODO: checkout should use branch completion
"""
import os
import IPython.ipapi

ip = IPython.ipapi.get()

def set_complete(func,key):
    ip.set_hook('complete_command', func, re_key=key)

def filesystem_completer(self,event):
    """ awkward, but cannot find a better way to do this.. """
    base = __IPYTHON__.complete(event.line.split()[-1])
    return [x for x in base if os.path.exists(x)]

class git(object):
    @property
    def local_branches(self):
        """ """
        return filter(None, map(lambda x: x.replace("*","").strip(),
                                os.popen('git branch -a|grep -v remote').readlines()))

    @property
    def subcommands(self):
        subs = ['add', 'bisect', 'branch', 'checkout',
                'cherry-pick', 'clone', 'commit', 'diff',
                'fetch', 'grep', 'init', 'log', 'merge',
                'mv', 'pull', 'push', 'rebase',
                'reset', 'rm', 'show', 'status', 'tag']
        return subs
git = git()


set_complete(lambda self, event: git.subcommands, 'git [\S]*$')
set_complete(lambda self, event: git.local_branches, 'git checkout')
set_complete(lambda self, event: git.local_branches, 'git push')
set_complete(filesystem_completer, 'git add')
set_complete(filesystem_completer, 'git mv')

def install_git_aliases():
    __IPYTHON__.magic_alias('grc git rebase --continue')
    __IPYTHON__.magic_alias('rebase git rebase -i')
    __IPYTHON__.magic_alias('checkout git checkout')
    __IPYTHON__.magic_alias('co git checkout')
    __IPYTHON__.magic_alias('st git status')
    __IPYTHON__.magic_alias('gd git diff --color')
    __IPYTHON__.magic_alias('gc git commit')
