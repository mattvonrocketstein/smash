""" SmaSh plugin that describes a reader/opener for emacs ~/.recentf
"""
import re, os

from smash.plugins import SmashPlugin

R_QUOTED = re.compile(r'".*"')
RECENTF_FILE = os.path.expanduser('~/.recentf')

class RecentF(object):

    command_name = 'recentf'

    @property
    def _file_paths(self):
        """ has to get .recentf contents with a regex
            since this file is written in a elisp format
        """
        contents = open(RECENTF_FILE, 'r').read()
        file_paths = R_QUOTED.findall(contents)
        file_paths = [ x[1:-1] for x in file_paths ]
        return file_paths

    @property
    def __doc__(self):
        main=("Recent files according to emacs {0} are listed below.\n"
              "To open the Nth entry, just type \"{1}[N]\".\n\n")
        main=main.format(RECENTF_FILE, self.command_name)
        file_paths = self._file_paths
        out = []
        for fpath in file_paths:
            out.append('{0}: "{1}"'.format(file_paths.index(fpath),fpath))
        return main + '\n'.join(out)

    def _open_rfile(self,f):
        os.system('emacsclient -n {0}'.format(f))

    def __getitem__(self, n):
        f = self._file_paths[n]
        self._open_rfile(f)
        return f

class Plugin(SmashPlugin):
    """ usage:
          to get an ordered list of recent files:
            $ recentf?

          to open one of them from the list:
            $ recentf[i]
    """

    name = 'EmacsRecentFilePlugin'

    def install(self):
        self.contribute(RecentF.command_name, RecentF())
