""" smashlib.handle
"""

from smashlib import get_smash

class AbstractInterface(object):

    """ """

    _user_ns_var = None

    def __init__(self, parent):
        self._parent = parent
        self._parent.__class__.interface = self
        get_smash().shell.user_ns[self._user_ns_var] = self

    def __repr__(self):
        return "{0} bound to {1}.  Use '{2}?' for more information".format(
            self.__class__.__name__,
            self._parent.__class__.__name__,
            self._user_ns_var
            )

    __str__ = __repr__

    @property
    def __doc__(self):
        self.update()

    @property
    def edit(self):
        raise RuntimeError("edit not defined for {0}".format(self))
