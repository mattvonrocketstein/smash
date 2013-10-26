""" smash_cmd__link

    adds the "link" command to smash.

    i can never remember the order of arguments for "ln -s x y",
    this version determines the link source by decided which of the
    arguments does not already exist.  (it is an error for "link x y"
    if "x" and "y" both exists)

"""

from smashlib.plugins import SmashPlugin

def link(x, y):
    assert ope(x) ^ ope(y)
    target = x if not ope(x) else y
    source = x if ope(x) else y
    os.system("ln -s {0} {1}".format(source, target))

class Plugin(SmashPlugin):
    def install(self):
        self.contribute_magic('link', link)
