""" ipy_smash_aliases

    general shell aliases.  this stuff is somewhat idiosyncratic
    to my own needs, but it's kind of just a place to throw your
    old bash aliases so transitioning to smash isn't too painful

    TODO: these aliases may not survive a "rehash" when proj is activated?
"""

def install_aliases():
    __IPYTHON__.magic_alias('dhclient sudo dhclient')
    __IPYTHON__.magic_alias('dad django-admin.py')
    __IPYTHON__.magic_alias('ls ls --color=auto')
    __IPYTHON__.magic_alias('apt-get sudo apt-get')

if __name__=='__smash__':
    install_aliases()
