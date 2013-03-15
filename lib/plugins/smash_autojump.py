""" smash_autojump
"""

import os
import smashlib
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import post_hook_for_magic
from smashlib.util import report, report_if_verbose, _ip, set_complete

DEFAULT_DATA_FILE = 'autojump.dat'

def j_completer(db, himself, event):
    path_elements = [ ]
    for x in db.data.keys():
        path_elements += x.split(os.path.sep)
    path_elements = list(set(filter(None, path_elements)))
    return path_elements

class Plugin(SmashPlugin):

    @property
    def datafile(self):
        return opj(smashlib._meta['tmp_dir'], DEFAULT_DATA_FILE)

    def touch_datafile(self):
        with open(self.datafile,'w') as handle:
            pass

    def add_or_increment_weight(self):
        """ useful as a post-hook for "cd" commands. it might be
            a good idea to call this after the "jump" command or
            after "pushd" as well, but that's not implemented.
        """
        if self.is_updating:
            path = os.getcwd()
            self.db.add(path)
            report.autojump("incremented jump-weight for '{0}' to {1}".format(
                path,self.db.data[path]))

    def install(self):
        self.set_env('AUTOJUMP_DATA_DIR', smashlib._meta['tmp_dir'])
        # do not move this import (it relies on the set_senv() call)
        from smashlib.contrib.autojump import Database, find_matches
        if not ope(self.datafile): self.touch_datafile()
        self.db = Database(self.datafile)

        # auto-increment weight for dirs that are used with 'cd ..'
        post_hook_for_magic('cd', self.add_or_increment_weight)

        # define and bind the "j" command (short for jump)
        def j(_dir):
            if not _dir:
                print self.db.data
            else:
                matches = find_matches(self.db, [_dir])
                if matches:
                    chose = matches[0]
                    report.autojump('from {0} matches, chose "{1}"'.format(
                        len(matches),chose))
                    #os.chdir(chose)
                    self.is_updating = False
                    __IPYTHON__.ipmagic('pushd '+chose)
                    self.is_updating = True
                else:
                    report.autojump("no matches found.")
        self.contribute_magic('j', j)
        self.contribute_magic('jump', j)
        self.contribute('db', self.db)

        # turns on the automatic weight-updating.
        self.is_updating = True
        fxn = lambda himself,event: j_completer(self.db, himself, event)
        set_complete(fxn, 'j')
