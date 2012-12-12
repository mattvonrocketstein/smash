""" smashlib.aliases
"""
from types import StringTypes
from collections import defaultdict, namedtuple

from smashlib.smash_plugin import SmashPlugin


class Alias(namedtuple('Alias', 'alias affiliation'.split())):
    pass


class RegistrationList(list):
    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__,
                                   list.__repr__(self))
    def keys(self):
        return list(set([x.affiliation for x in self]))

    def __getitem__(self, project_name):
        """ filter by project_name """
        out = []
        for x in self:
            if x.affiliation == project_name:
                out.append(x.alias)
        return out


class Aliases(RegistrationList):

    def install(self):
        """ install known all known aliases into this IPython instance """
        [ __IPYTHON__.magic_alias(alias.alias) for alias in self ]

    def uninstall(self, alias):
        """ uninstall known all known aliases into this IPython instance """
        if isinstance(alias, StringTypes):
            return __IPYTHON__.magic_unalias(alias.split()[0])
        raise Exception,'niy'+str(alias)

    def add(self, full_alias, project='__smash__'):
        """ adds an alias to registry, optionally with a project affiliation """
        item = Alias(alias=full_alias, affiliation=project)
        if item not in self:
            self.append(item)
        return item
