""" ipy_smash_aliases

    general shell aliases.  this stuff is somewhat idiosyncratic
    to my own needs, but it's kind of just a place to throw your
    old bash aliases so transitioning to smash isn't too painful

    TODO: these aliases may not survive a "rehash" when proj is activated?
"""


def install_aliases():
    __IPYTHON__.magic_alias('dhclient sudo dhclient')
    __IPYTHON__.magic_alias('apt-get sudo apt-get')
    __IPYTHON__.magic_alias('dad django-admin.py')
    __IPYTHON__.magic_alias('ls ls --color=auto')

    # avoid an unpleasant surprise: patch reset to clean up the display like bash, not reset the namespace.
    from IPython.Magic import Magic
    def reset(himself, parameter_s=''):
        __IPYTHON__.system('reset')
        return 'overridden'
    Magic.magic_reset = reset

if __name__=='__smash__':
    install_aliases()
