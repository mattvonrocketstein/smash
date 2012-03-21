## general shell aliases.  this stuff is somewhat idiosyncratic, but it seems
## like if it's not relevant it simply won't be used.  no harm no foul.
## TODO: these aliases do not survive a "rehash" when proj is activated. damn
################################################################################
def install_aliases():
    __IPYTHON__.magic_alias('dhclient sudo dhclient')
    __IPYTHON__.magic_alias('dad django-admin.py')
    __IPYTHON__.magic_alias('ls ls --color=auto')
    __IPYTHON__.magic_alias('apt-get sudo apt-get')
