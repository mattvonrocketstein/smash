"""
ipy_git_completers
"""
import os
import IPython.ipapi

ip = IPython.ipapi.get()

class git(object):
    @property
    def local_branches(self):
        """ """
        return map(lambda x: x.replace("*","").strip(),
                   os.popen('git branch -a|grep -v remote').readlines())

    @property
    def subcommands(self):
        subs = ['add',
                'bisect',
                'branch',
                'checkout',
                'clone',
                'commit',
                'diff',
                'fetch',
                'grep',
                'init',
                'log',
                'merge',
                'mv',
                'pull',
                'push',
                'rebase',
                'reset',
                'rm',
                'show',
                'status',
                'tag']
        return subs
git = git()

ip.set_hook('complete_command',lambda self,event: git.subcommands,
            re_key='git')
ip.set_hook('complete_command',lambda self,event: git.local_branches,
            re_key='git checkout')
