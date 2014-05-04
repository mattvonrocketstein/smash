""" smash.data
"""

from IPython import ipapi
from smashlib.util import _ip
ip = _ip()

## various overrides for patching ip.options. doing it here puts as much code as
## possible actually in pure python instead of in ipython's weird rc format file
################################################################################
OVERRIDE_OPTIONS = dict(
    autoedit_syntax=1,
    confirm_exit = 0,

    # there is a bug with autocall where it can execute properties
    # twice.  very annoying since plugins rely on that heavily
    # for e.g. "obj?" style help menus, etc
    autocall=0,

    # TODO: this should really be part of the git plugin.
    # TODO: see smash.util.set_prompt_t for changing prompt on the fly
    #prompt_in1= PROMPT_DEFAULT,

    include = list(set(ip.options.include + ['ipythonrc-pysh',
                                             'ipythonrc-git-aliases',
                                             'ipythonrc-bash-aliases', ])),

    # 'complete' only completes as much as possible while
    # 'menu-complete'  cycles through all possible completions.
    # readline_parse_and_bind tab: menu-complete
    readline_parse_and_bind = list(set(ip.options.readline_parse_and_bind + \
                              ['tab: complete',
                               '"\C-l": clear-screen',      # control+L
                               #'"\H": backward-kill-word',  # control+delete
                               '"\C-?": backward-kill-word',  # control+delete
                               ])),

    # readline_omit__names 1: omit showing any names starting with two __
    # readline_omit__names 2: completion will omit all names beginning with _
    # Note that, regardless, typing a _ AFTER a period and hitting <tab>
    # will ALWAYS complete attribute names starting with '_'; in other words
    # these settings seem to only affect the global namespace.
    readline_omit__names = 1,
)
