"""smashlib.handle
"""


class AbstractInterface(object):

    """ """
    user_ns_var = None

    def __repr__(self):
        return self.__class__.__name__

    __str__ = __repr__

    def __init__(self, smash):
        self.smash = smash

    @property
    def __doc__(self):
        self.update()

    @property
    def edit(self):
        raise RuntimeError("edit not defined for {0}".format(self))
