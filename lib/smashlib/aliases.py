""" smashlib.aliases
"""
from types import StringTypes
from collections import defaultdict, namedtuple

from smashlib.smash_plugin import SmashPlugin
from smashlib.util import (list2table, colorize,
                           report, report_if_verbose)

def add_new_aliases(bus, name=None):
    """ this function will be attached to the post-activation signal """
    from smashlib.projects import Project
    from smashlib import ALIASES as aliases
    report.alias_manager('adding new aliases for "{0}"'.format(name))
    new_aliases = aliases[name]
    count = [ aliases.add(a, name) for a in new_aliases ]
    if count:
        msg = "\tadded {0} aliases for this project".format(len(count))
        report.alias_manager(msg)
    report.project_manager('resetting CURRENT_PROJECT')
    Project.CURRENT_PROJECT = name

def kill_old_aliases(bus, name=None):
    """ this function will be attached to the pre-activation signal """
    #ignore what came in because it's really the new project
    from smashlib.projects import Project, NO_ACTIVE_PROJECT
    name = Project.CURRENT_PROJECT
    if name==NO_ACTIVE_PROJECT:
        return
    from smashlib import ALIASES as aliases
    report.alias_manager('killing old aliases for "{0}"'.format(name))
    old_aliases = aliases[name]
    count = [ [aliases.remove(aliases.full_alias_to_item(a)),
               aliases.uninstall(a)] for a in old_aliases ]
    if count:
        msg = "removed {0} aliases from the previous project"
        msg = msg.format(len(count))
        report.alias_manager(msg)

def rehash_aliases(bus,*args,**kargs):
    report.alias_manager('rehashing aliases.')
    import smashlib
    aliases = getattr(smashlib, 'ALIASES')
    aliases.install()


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

    @staticmethod
    def _sort_aliases(x,y):
        t1 = cmp(x.affiliation, y.affiliation)
        if t1==0:
            t1 = cmp(x.alias, y.alias)
        return t1

    def __qmark__(self):
        from smashlib import ALIASES as aliases
        lst = [x for x in aliases]
        lst.sort(self._sort_aliases)
        dat=[]
        headers = 'group alias command'.split()
        for alias in aliases:
            nick = alias.alias.split(' ')[0]
            cmd = ' '.join(alias.alias.split(' ')[1:])
            dat.append([alias.affiliation, nick, cmd])
        report(colorize("{red}SmaSh aliases:{normal}\n\n") + list2table(dat, headers))

    def install(self):
        """ install known all known aliases into this IPython instance """
        [ __IPYTHON__.magic_alias(alias.alias) for alias in self ]

    def uninstall(self, alias):
        """ uninstall known all known aliases into this IPython instance """
        report_if_verbose.alias_manager('uninstalling, ' + str(alias))
        if isinstance(alias, StringTypes):
            return __IPYTHON__.magic_unalias(alias.split()[0])
        raise NotImplemented('niy' + str(alias))

    def full_alias_to_item(self, full_alias):
        return [x for x in self if x.alias==full_alias][0]

    def add(self, full_alias, project='__smash__'):
        """ adds an alias to registry, optionally with a project affiliation """
        item = Alias(alias=full_alias, affiliation=project)
        if item not in self:
            self.append(item)
        return item
