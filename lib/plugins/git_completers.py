""" git_completers

    WARNING:
    most of this stuff fails silently and ipython mangles scope on the hooks you
    register, so for instance DO NOT attempt to abstract local variables out of
    your handle functions unless you really know what you're doing.  no idea wtf
    ipython does that or how to work around it.

    TODO: smarter with ?http://pypi.python.org/pypi/gitinfo/0.0.2 ?
          depends on GitPython, which is largeish
    TODO: 'git diff'' should use branch completion AND fs-completion
    TODO: 'git push' should complete from the names of the remotes
    TODO: 'git push <remote>' should complete from the names of local_branches()
    TODO: consider .gitignore ?
"""
import os
import IPython.ipapi

from smashlib.util import report, set_complete
from smashlib.smash_plugin import SmashPlugin

def uncomitted_files_completer(self, event):
    """ awkward, but cannot find a better way to do this.. """
    lines = os.popen('git status|grep modified').readlines()
    sys_output = [ x.strip()[2:].split()[-1] for x in lines ]
    return sys_output

def fsc_utfc(self, event):
    """ filesystem-completer + untracked_files-completer """
    return filesystem_completer(self, event) + \
           untracked_files_completer(self,event)

def untracked_files_completer(self, event):
    lines = os.popen('git status').readlines()
    begin = None
    for line in lines:
        if 'Untracked files:' in line:
            begin = lines.index(line)
    if begin is None:
        return []
    lines = lines[begin:]
    lines = [line for line in lines if line.startswith('#\t')]
    lines = [ line.strip().replace('\t','')[1:] for line in lines ]
    return lines

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
        r = [ x for x in base if os.path.exists(x) ]
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

class Plugin(SmashPlugin):
    GIT_ALIASES = [ 'grm git rebase -i origin/master',
                    'grc git rebase --continue',
                    'gra git rebase --abort',
                    'checkout git checkout',
                    'rebase git rebase -i',
                    'gc git commit',
                    'gd git diff --color',
                    'st git status',
                    'co git checkout',
                    ('vlog git log --graph --date-order --date=relative --color'),]


    def install(self):
        from smashlib import ALIASES as aliases
        [ aliases.add(x, '__git_plugin__') for x in self.GIT_ALIASES ]
        aliases.install()

        report.git_completer('setting prompt to use git vcs')
        __IPYTHON__._cgb = lambda : os.popen("current_git_branch").read().strip()
        set_complete(local_branches, 'git checkout')
        set_complete(subcommands, 'git [\S]*$')
        set_complete(filesystem_completer, 'git mv')
        set_complete(uncomitted_files_completer, 'git commit')
        set_complete(uncomitted_files_completer, 'gd')
        set_complete(uncomitted_files_completer, 'git diff')
        set_complete(local_branches, 'git merge')
        set_complete(local_branches, 'git log')
        #set_complete(lambda self, event: git.local_branches, 'git push')

        # TODO: .. only need file-system if in the middle of rebase ..
        set_complete(fsc_utfc, 'git add')
