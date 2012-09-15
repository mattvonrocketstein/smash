""" ipy_git_completers

    WARNING:
    most of this stuff fails silently and ipython mangles scope on the hooks you
    register, so for instance DO NOT attempt to abstract local variables out of
    your handle functions unless you really know what you're doing.  no idea wtf
    ipython does that or how to work around it.

    TODO: 'git diff'' should use branch completion AND fs-completion
    TODO: 'git push' should complete from the names of the remotes
    TODO: 'git push <remote>' should complete from the names of local_branches()
"""
import os
import IPython.ipapi
from smash.util import report
ip = IPython.ipapi.get()


def set_complete(func, key):
    report.git('setting hook'+str([func,ip]))
    ip.set_hook('complete_command', func, re_key=key)

def filesystem_completer(self, event):
    """ awkward, but cannot find a better way to do this.. """
    data = event.line.split()[2:] # e.g. 'git',' mv', './<tab>'

    # no info: complete from the contents of the wd
    if not data:
        return os.listdir(os.getcwd())

    # started typing something.. leverage ipython's completion
    else:
        data = data[-1]
        base = __IPYTHON__.complete(data)
        r = [x for x in base if os.path.exists(x)]
        return r

def local_branches(*args, **kargs):
    """ """
    all_branches_cmd = 'git branch -a|grep -v remote'
    return filter(None, map(lambda x: x.replace("*","").strip(),
                            os.popen(all_branches_cmd).readlines()))

def subcommands(*args, **kargs):
    # WOW.. be careful!
    # this doesn't work if you take GIT_SUBCOMMANDS out of the function.
    # ipython is somehow, for some reason, mangling scope for the handlers
    # this is particularly nasty because it seems it fails totally silently
    GIT_SUBCOMMANDS = ['add', 'bisect', 'branch', 'checkout',
                   'cherry-pick', 'clone', 'commit', 'diff',
                   'fetch', 'grep', 'init', 'log', 'merge',
                   'mv', 'pull', 'push', 'rebase',
                   'reset', 'rm', 'show', 'status', 'tag']

    return GIT_SUBCOMMANDS


def install_git_aliases():
    GIT_ALIASES = [ 'grm git rebase -i origin/master',
                    'grc git rebase --continue',
                    'checkout git checkout',
                    'rebase git rebase -i',
                    'gc git commit',
                    'gd git diff --color',
                    'st git status','co git checkout', ]
    from smash import aliases
    [ aliases.add(x, '__git_plugin__') for x in GIT_ALIASES ]
    aliases.install()

if __name__=='__smash__':
    install_git_aliases()
    report('setting prompt to use git vcs')
    __IPYTHON__._cgb = lambda : os.popen("current_git_branch").read().strip()
    set_complete(local_branches, 'git checkout')
    set_complete(subcommands, 'git [\S]*$')

    #set_complete(lambda self, event: git.local_branches, 'git push')
    set_complete(filesystem_completer, 'git add')
    set_complete(filesystem_completer, 'git mv')
