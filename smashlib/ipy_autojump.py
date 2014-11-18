""" smash_autojump

    Adds the magic 'j' or 'jump' command, which tracks and weights every time
    you change directory.

    Basically 'j some_specific_director<tab>' will be made to complete from a
    list or places that are already remembered from prior usage patterns (some
    of which might be really hard to type the absolute path for).
"""

import os
import smashlib
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import post_hook_for_magic
from smashlib.util import report, report_if_verbose, _ip, set_complete

DEFAULT_DATA_FILE = 'autojump.dat'

def j_completer(db, himself, event):
    """ TODO: longest-common-substring algorithm
              etc for even smarter completions """
    path_elements = [ ]
    for x in db.data.keys():
        path_elements += x.split(os.path.sep)
    path_elements = list(set(filter(None, path_elements)))
    return path_elements

def touch_file(_file):
    with open(_file, 'w') as handle:
        pass

class Plugin(SmashPlugin):

    @property
    def datafile(self):
        return opj(smashlib._meta['tmp_dir'], DEFAULT_DATA_FILE)

    def touch_datafile(self):
        touch_file(self.datafile)

    def add_or_increment_weight(self):
        """ useful as a post-hook for "cd" commands. it might be
            a good idea to call this after the "jump" command or
            after "pushd" as well, but that's not implemented.
        """
        if self.is_updating:
            path = os.getcwd()
            self.db.add(path)
            report_if_verbose.autojump(
                "incremented jump-weight for '{0}' to {1}".format(
                    path,self.db.data[path]))

    def install(self):
        self.set_env('AUTOJUMP_DATA_DIR', smashlib._meta['tmp_dir'])
        # do not move this import (it relies on the set_senv() call)
        from smashlib.contrib.autojump import Database, find_matches
        if not ope(self.datafile):
            self.touch_datafile()
        self.db = Database(self.datafile)

        # auto-increment weight for dirs that are used with 'cd ..'
        post_hook_for_magic('cd', self.add_or_increment_weight)

        # define and bind the "j" command (short for jump)
        # TODO: refactor and use a partial here
        def j(_dir):
            if not _dir:
                print self.db.data
            else:
                matches = find_matches(self.db, [_dir])
                if matches:
                    chose = matches[0]
                    report.autojump('from {0} matches, chose "{1}"'.format(
                        len(matches),chose))
                    self.is_updating = False
                    __IPYTHON__.ipmagic('pushd ' + chose)
                    self.is_updating = True
                else:
                    report.autojump("no matches found.")
        self.contribute_magic('j', j)
        self.contribute_magic('jump', j)
        self.contribute('db', self.db)

        # turns on the automatic weight-updating.
        self.is_updating = True
        fxn = lambda himself, event: j_completer(self.db, himself, event)
        set_complete(fxn, 'j')
