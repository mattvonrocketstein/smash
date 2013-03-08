#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Copyright © 2008-2012 Joel Schaerer
  Copyright © 2012      William Ting

  *  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3, or (at your option)
  any later version.

  *  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  *  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""

from __future__ import division, print_function

import sys
import os
try:
    import argparse
except ImportError:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    import autojump_argparse as argparse
    sys.path.pop()
from operator import itemgetter
import re
import shutil
from tempfile import NamedTemporaryFile

VERSION = 'release-v21.5.2'
MAX_KEYWEIGHT = 1000
MAX_STORED_PATHS = 1000
COMPLETION_SEPARATOR = '__'
ARGS = None

CONFIG_DIR = None
DB_FILE = None
TESTING = False

# load config from environmental variables
if 'AUTOJUMP_DATA_DIR' in os.environ:
    CONFIG_DIR = os.environ.get('AUTOJUMP_DATA_DIR')
else:
    xdg_data_dir = os.environ.get('XDG_DATA_HOME') or \
        os.path.join(os.environ['HOME'], '.local', 'share')
    CONFIG_DIR = os.path.join(xdg_data_dir, 'autojump')

KEEP_ALL_ENTRIES = False
if 'AUTOJUMP_KEEP_ALL_ENTRIES' in os.environ and \
        os.environ.get('AUTOJUMP_KEEP_ALL_ENTRIES') == '1':
    KEEP_ALL_ENTRIES = True

ALWAYS_IGNORE_CASE = False
if 'AUTOJUMP_IGNORE_CASE' in os.environ and \
        os.environ.get('AUTOJUMP_IGNORE_CASE') == '1':
    ALWAYS_IGNORE_CASE = True

KEEP_SYMLINKS = False
if 'AUTOJUMP_KEEP_SYMLINKS' in os.environ and \
        os.environ.get('AUTOJUMP_KEEP_SYMLINKS') == '1':
    KEEP_SYMLINKS = True

if CONFIG_DIR == os.path.expanduser('~'):
    DB_FILE = CONFIG_DIR + '/.autojump.txt'
else:
    DB_FILE = CONFIG_DIR + '/autojump.txt'

class Database:
    """
    Object for interfacing with autojump database.
    """

    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        self.load()

    def __len__(self):
        return len(self.data)

    def add(self, path, increment = 10):
        """
        Increase weight of existing paths or initialize new ones to 10.
        """
        if path not in self.data:
            self.data[path] = increment
        else:
            import math
            self.data[path] = math.sqrt((self.data[path]**2) + (increment**2))
        self.save()

    def decrease(self, path, increment = 15):
        """
        Decrease weight of existing path. Unknown ones are ignored.
        """
        if path in self.data:
            if self.data[path] < increment:
                self.data[path] = 0
            else:
                self.data[path] -= increment
            self.save()

    def decay(self):
        """
        Decay database entries.
        """
        for k in self.data.keys():
            self.data[k] *= 0.9

    def get_weight(self, path):
        """
        Return path weight.
        """
        if path in self.data:
            return self.data[path]
        else:
            return 0

    def load(self, error_recovery = False):
        """
        Try to open the database file, recovering from backup if needed.
        """
        if os.path.exists(self.filename):
            try:
                if sys.version_info >= (3, 0):
                    with open(self.filename, 'r', encoding = 'utf-8') as f:
                        for line in f.readlines():
                            weight, path = line[:-1].split("\t", 1)
                            path = decode(path, 'utf-8')
                            self.data[path] = float(weight)
                else:
                    with open(self.filename, 'r') as f:
                        for line in f.readlines():
                            weight, path = line[:-1].split("\t", 1)
                            path = decode(path, 'utf-8')
                            self.data[path] = float(weight)
            except (IOError, EOFError):
                self.load_backup(error_recovery)
        else:
            self.load_backup(error_recovery)

    def load_backup(self, error_recovery = False):
        """
        Loads database from backup file.
        """
        if os.path.exists(self.filename + '.bak'):
            if not error_recovery:
                print('Problem with autojump database,\
                        trying to recover from backup...', file=sys.stderr)
                shutil.copy(self.filename + '.bak', self.filename)
                return self.load(True)

    def maintenance(self):
        """
        Trims and decays database entries when exceeding settings.
        """
        if sum(self.data.values()) > MAX_KEYWEIGHT:
            self.decay()
        if len(self.data) > MAX_STORED_PATHS:
            self.trim()
        self.save()

    def purge(self):
        """
        Deletes all entries that no longer exist on system.
        """
        removed = []
        for path in self.data.keys():
            if not os.path.exists(path):
                removed.append(path)
                del self.data[path]
        self.save()
        return removed

    def save(self):
        """
        Save database atomically and preserve backup, creating new database if
        needed.
        """
        # check file existence and permissions
        if ((not os.path.exists(self.filename)) or
                os.name == 'nt' or
                os.getuid() == os.stat(self.filename)[4]):
            temp = NamedTemporaryFile(dir = CONFIG_DIR, delete = False)
            for path, weight in sorted(self.data.items(),
                    key=itemgetter(1),
                    reverse=True):
                temp.write((unico("%s\t%s\n")%(weight, path)).encode("utf-8"))

            # catching disk errors and skipping save when file handle can't
            # be closed.
            try:
                # http://thunk.org/tytso/blog/2009/03/15/dont-fear-the-fsync/
                temp.flush()
                os.fsync(temp)
                temp.close()
            except IOError as ex:
                print("Error saving autojump database (disk full?)" %
                        ex, file=sys.stderr)
                return

            shutil.move(temp.name, self.filename)
            try: # backup file
                import time
                if (not os.path.exists(self.filename+".bak") or
                        time.time()-os.path.getmtime(self.filename+".bak") \
                                > 86400):
                    shutil.copy(self.filename, self.filename+".bak")
            except OSError as ex:
                print("Error while creating backup autojump file. (%s)" %
                        ex, file=sys.stderr)

    def trim(self, percent=0.1):
        """
        If database has exceeded MAX_STORED_PATHS, removes bottom 10%.
        """
        dirs = list(self.data.items())
        dirs.sort(key=itemgetter(1))
        remove_cnt = int(percent * len(dirs))
        for path, _ in dirs[:remove_cnt]:
            del self.data[path]


def options():
    """
    Parse command line options.
    """
    global ARGS

    parser = argparse.ArgumentParser(
            description='Automatically jump to \
            directory passed as an argument.',
            epilog="Please see autojump(1) man pages for full documentation.")
    parser.add_argument(
            'directory', metavar='DIRECTORY', nargs='*', default='',
            help='directory to jump to')
    parser.add_argument(
            '-a', '--add', '--increase', metavar='DIRECTORY',
            help='manually add path to database, or increase path weight for \
            existing paths')
    parser.add_argument(
            '-d', '--decrease', metavar='WEIGHT', nargs='?', type=int,
            const=15, default=False,
            help='manually decrease path weight in database')
    parser.add_argument(
            '-b', '--bash', action="store_true", default=False,
            help='enclose directory quotes to prevent errors')
    parser.add_argument(
            '--complete', action="store_true", default=False,
            help='used for tab completion')
    parser.add_argument(
            '--purge', action="store_true", default=False,
            help='delete all database entries that no longer exist on system')
    parser.add_argument(
            '-s', '--stat', action="store_true", default=False,
            help='show database entries and their key weights')
    parser.add_argument(
            '-v', '--version', action="version", version="%(prog)s " + VERSION,
            help='show version information and exit')

    ARGS = parser.parse_args()

    # The home dir can be reached quickly by "cd" and may interfere with other
    # directories
    if (ARGS.add):
        if(ARGS.add != os.path.expanduser("~")):
            db = Database(DB_FILE)
            db.add(decode(ARGS.add))
        return True

    if (ARGS.decrease):
        if(ARGS.decrease != os.path.expanduser("~")):
            db = Database(DB_FILE)
            # FIXME: handle symlinks?
            db.decrease(os.getcwd(), ARGS.decrease)
        return True

    if (ARGS.purge):
        db = Database(DB_FILE)
        removed = db.purge()
        if len(removed) > 0:
            for dir in removed:
                output(unico(dir))
        print("Number of database entries removed: %d" % len(removed))
        return True

    if (ARGS.stat):
        db = Database(DB_FILE)
        dirs = list(db.data.items())
        dirs.sort(key=itemgetter(1))
        for path, count in dirs[-100:]:
            output(unico("%.1f:\t%s") % (count, path))

        print("________________________________________\n")
        print("%d:\t total key weight" % sum(db.data.values()))
        print("%d:\t stored directories" % len(dirs))
        print("db file: %s" % DB_FILE)
        return True
    return False

def decode(text, encoding=None, errors="strict"):
    """
    Decoding step for Python 2 which does not default to unicode.
    """
    if sys.version_info[0] > 2:
        return text
    else:
        if encoding is None:
            encoding = sys.getfilesystemencoding()
        return text.decode(encoding, errors)

def output(unicode_text, encoding=None):
    """
    Wrapper for the print function, using the filesystem encoding by default
    to minimize encoding mismatch problems in directory names.
    """
    if sys.version_info[0] > 2:
        print(unicode_text)
    else:
        if encoding is None:
            encoding = sys.getfilesystemencoding()
        print(unicode_text.encode(encoding))

def unico(text):
    """
    If Python 2, convert to a unicode object.
    """
    if sys.version_info[0] > 2:
        return text
    else:
        return unicode(text)

def match_last(pattern):
    """
    If the last pattern contains a full path, jump there.
    The regexp is because we need to support stuff like
    "j wo jo__3__/home/joel/workspace/joel" for zsh.
    """
    last_pattern_path = re.sub("(.*)"+COMPLETION_SEPARATOR, "", pattern[-1])
    if (len(last_pattern_path) > 0 and
            last_pattern_path[0] == "/" and
            os.path.exists(last_pattern_path)):
        if not ARGS.complete:
            output(last_pattern_path)
            return True
    return False

def match(path, pattern, only_end=False, ignore_case=False):
    """
    Check whether a path matches a particular pattern, and return
    the remaining part of the string.
    """
    if only_end:
        match_path = "/".join(path.split('/')[-1-pattern.count('/'):])
    else:
        match_path = path

    if ignore_case:
        match_path = match_path.lower()
        pattern = pattern.lower()

    find_idx = match_path.find(pattern)
    # truncate path to avoid matching a pattern multiple times
    if find_idx != -1:
        return (True, path)
    else:
        return (False, path[find_idx+len(pattern):])

def find_matches(db, patterns, max_matches=1, ignore_case=False, fuzzy=False):
    """
    Find max_matches paths that match the pattern, and add them to the
    result_list.
    """
    try:
        current_dir = decode(os.path.realpath(os.curdir))
    except OSError:
        current_dir = None

    dirs = list(db.data.items())
    dirs.sort(key=itemgetter(1), reverse=True)
    results = []
    if fuzzy:
        from difflib import get_close_matches

        # create dictionary of end paths to compare against
        end_dirs = {}
        for d in dirs:
            if ignore_case:
                end = d[0].split('/')[-1].lower()
            else:
                end = d[0].split('/')[-1]

            # collisions: ignore lower weight paths
            if end not in end_dirs:
                end_dirs[end] = d[0]

        # find the first match (heighest weight)
        while True:
            found = get_close_matches(patterns[-1], end_dirs, n=1, cutoff=.6)
            if not found:
                break
            # avoid jumping to current directory
            if (os.path.exists(found[0]) or TESTING) and \
                current_dir != os.path.realpath(found[0]):
                break
            # continue with the last found directory removed
            del end_dirs[found[0]]

        if found:
            found = found[0]
            results.append(end_dirs[found])
            return results
        else:
            return []

    current_dir_match = False
    for path, _ in dirs:
        found, tmp = True, path
        for n, p in enumerate(patterns):
            # for single/last pattern, only check end of path
            if n == len(patterns)-1:
                found, tmp = match(tmp, p, True, ignore_case)
            else:
                found, tmp = match(tmp, p, False, ignore_case)
            if not found: break

        if found and (os.path.exists(path) or TESTING):
            # avoid jumping to current directory
            # (call out to realpath this late to not stat all dirs)
            if current_dir == os.path.realpath(path):
                current_dir_match = True
                continue

            if path not in results:
                results.append(path)
            if len(results) >= max_matches:
                break

    # if current directory is the only match, add it to results
    if len(results) == 0 and current_dir_match:
        results.append(current_dir)

    return results

def shell_utility():
    """
    Run this when autojump is called as a shell utility.
    """
    if options(): return True
    db = Database(DB_FILE)

    # if no directories, add empty string
    if (ARGS.directory == ''):
        patterns = [unico('')]
    else:
        patterns = [decode(a) for a in ARGS.directory]

    # check last pattern for full path
    # FIXME: disabled until zsh tab completion is fixed on the shell side
    # if match_last(patterns): return True

    # check for tab completion
    tab_choice = -1
    tab_match = re.search(COMPLETION_SEPARATOR+"([0-9]+)", patterns[-1])
    if tab_match: # user has selected a tab completion entry
        tab_choice = int(tab_match.group(1))
        patterns[-1] = re.sub(COMPLETION_SEPARATOR+"[0-9]+.*", "", patterns[-1])
    else: # user hasn't selected a tab completion, display choices again
        tab_match = re.match("(.*)"+COMPLETION_SEPARATOR, patterns[-1])
        if tab_match:
            patterns[-1] = tab_match.group(1)

    # on tab completion always show all results
    if ARGS.complete or tab_choice != -1:
        max_matches = 9
    else:
        max_matches = 1

    results = []
    if not ALWAYS_IGNORE_CASE:
        results = find_matches(db, patterns, max_matches, ignore_case=False)

    # if no results, try ignoring case
    if ARGS.complete or not results:
        results = find_matches(db, patterns, max_matches, ignore_case=True)

    # if no results, try approximate matching
    if not results:
        results = find_matches(db, patterns, max_matches, ignore_case=True,
                fuzzy=True)

    quotes = ""
    if ARGS.complete and ARGS.bash: quotes = "'"

    if tab_choice != -1:
        if len(results) > tab_choice-1:
            output(unico("%s%s%s") % (quotes,results[tab_choice-1],quotes))
    elif len(results) > 1 and ARGS.complete:
        output("\n".join(("%s%s%d%s%s" % (patterns[-1],
            COMPLETION_SEPARATOR, n+1, COMPLETION_SEPARATOR, r)
            for n, r in enumerate(results[:8]))))
    elif results:
        output(unico("%s%s%s")%(quotes,results[0],quotes))
    else:
        return False

    if not KEEP_ALL_ENTRIES:
        db.maintenance()

    return True

if __name__ == "__main__":
    if not shell_utility():
        sys.exit(1)
