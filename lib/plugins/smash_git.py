""" git_completers

    Adds lots of git tab completion:

    And a few utilities:
      Type any of these commands follows "?" to read help about them:
        "clone_gist"
"""

"""    WARNING:
      most of this stuff fails silently and ipython mangles scope on the hooks
      you register, so for instance DO NOT attempt to abstract local variables
      out of your handle functions unless you really know what you're doing.
      no idea wtf ipython does that or how to work around it.

    TODO: smarter with ?http://pypi.python.org/pypi/gitinfo/0.0.2 ?
          depends on GitPython, which is largeish
    TODO: 'git diff'' should use branch completion AND fs-completion
    TODO: completion for e.g. 'git push origin XYZ'
    TODO: 'git push' should complete from the names of the remotes
    TODO: consider .gitignore ?
    TODO: 'git add' could be smarter if i could detect rebase state
    TODO: format-patch isn't completed
    useful- __IPYTHON__.shell.Completer.custom_completers.regexs

"""
import os
from IPython.macro import Macro

from smashlib.prompt import prompt, PromptComponent
from smashlib.python import expanduser
from smashlib.util import report, set_complete
from smashlib.smash_plugin import SmashPlugin

def clone_gist(parameter_s=''):
    cmd  = 'git clone git@gist.github.com:{0}.git {1}'
    args = parameter_s.split()
    assert args
    if len(args)==1: args+=['']
    cmd = cmd.format(*args)
    print '\t', cmd
    __IPYTHON__.system(cmd)

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

def reset_completer(self, event):
    options = '--patch --soft --mixed --hard --merge --keep'.split()
    return options

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

def remote_branches_completer(self, event):
    all_branches_cmd = 'git branch -a|grep remote'
    tmp = os.popen(all_branches_cmd).readlines()
    tmp = [x.split()[0].strip() for x in tmp if x]
    tmp = [x.replace("remotes/",'') for x in tmp ]
    return tmp

def local_branches(self, event):
    if event.symbol.startswith('origin'):
        return remote_branches_completer(self, event)
    all_branches_cmd = 'git branch -a|grep -v remote'
    return ['HEAD', 'origin/'] + \
               filter(None, map(lambda x: x.replace("*","").strip(),
                                os.popen(all_branches_cmd).readlines()))

def subcommands(*args, **kargs):
    # WOW.. be careful!
    # this doesn't work if you take GIT_SUBCOMMANDS out of the function.
    # ipython is somehow, for some reason, mangling scope for the handlers
    # this is particularly nasty because it seems it fails totally silently
    GIT_SUBCOMMANDS = ['add', 'bisect', 'blame', 'branch', 'checkout',
                       'cherry-pick', 'clone', 'commit', 'diff',
                       'fetch', 'grep', 'init', 'log', 'merge',
                       'mv', 'pull', 'push', 'rebase',
                       'reset', 'rm', 'show', 'status', 'tag']

    return GIT_SUBCOMMANDS

def fsc2(self, event):
    """ better file system completer that uses the working
        directory. the other code should probably use this..
    """
    return __IPYTHON__.Completer.file_matches(event.symbol)

class Plugin(SmashPlugin):
    GIT_ALIASES = [ 'grm git rebase -i origin/master',
                    'grc git rebase --continue',
                    'gra git rebase --abort',
                    'checkout git checkout',
                    'rebase git rebase -i',
                    'gs git show --color',
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
        cgb_path = expanduser(opj('~','bin',"current_git_branch"))
        __IPYTHON__._cgb = lambda: os.popen(cgb_path).read().strip()
        prompt.add(
            PromptComponent(name=self.filename,
                            priority=2,
                            template='''\C_Red${getattr(__IPYTHON__,'_cgb',lambda:'')()}'''))
        set_complete(local_branches, 'git checkout [\S]*$')
        set_complete(fsc2, 'git checkout [\S]* ')
        set_complete(fsc2, 'git rm')
        set_complete(subcommands, 'git [\s]*[\S]*$')
        set_complete(filesystem_completer, 'git mv')
        set_complete(uncomitted_files_completer, 'git commit')
        set_complete(uncomitted_files_completer, 'gd')
        set_complete(uncomitted_files_completer, 'git diff')
        set_complete(local_branches, 'git merge')
        set_complete(local_branches, 'git log')
        set_complete(reset_completer,'git reset')
        set_complete(local_branches, 'git reset --.* ')
        set_complete(local_branches, 'git rebase .* ')
        #set_complete(lambda self, event: git.local_branches, 'git push')

        # TODO: .. only need file-system if in the middle of rebase ..
        set_complete(fsc_utfc, 'git add')
        self.contribute_magic('clone_gist', clone_gist)
