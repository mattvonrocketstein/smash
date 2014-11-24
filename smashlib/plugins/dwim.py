""" smashlib.plugins.dwim

    documentation: http://mattvonrocketstein.github.io/smash/plugins.html#dwim
"""
import os

from IPython.utils.traitlets import Bool

from smashlib.v2 import Reporter
from smashlib.util.events import receives_event
from smashlib.channels import C_FAIL, C_FILE_INPUT
from IPython.utils.traitlets import EventfulDict
class DoWhatIMean(Reporter):
    """ """

    verbose=True

    automatic_cd = Bool(
        True, config=True,
        help="change directory if input looks like path name")
    automatic_edit = Bool(
        True, config=True,
        help="edit (small) files if input looks like file name")
    automatic_connect = Bool(
        True, config=True,
        help="connect automatically if input matches something in hosts-file")
    automatic_open = Bool(
        True, config=True,
        help="open automatically if input looks like webpage")
    suffix_aliases = EventfulDict(default_value={}, config=True)

    @receives_event(C_FILE_INPUT)
    def on_file_input(self, fpath):
        from smashlib.python import splitext, ope, abspath, expanduser
        fpath = abspath(expanduser(fpath))
        suffix = splitext(fpath)[-1][1:].lower()
        if ope(fpath):
            opener = self.suffix_aliases.get(
                suffix, None)
            if opener is not None:
                self.report('Using opener "{0}" for "{1}"'.format(opener, suffix))
                self.smash.shell.run_cell('{0} {1}'.format(opener, fpath))
            else:
                msg = "Legit file input, but no suffix alias could be found for "+suffix
                self.report(msg)
        else:
            msg = "Attempted file input, but path {0} does not exist".format(fpath)
            self.report(msg)

    def init(self):
        def smash_open(x):
            import webbrowser
            webbrowser.open(x)
        self.contribute_magic(smash_open)
        if self.automatic_cd or self.automatic_edit:
            self.smash.error_handlers.append(self.handle_NameError)

    def handle_NameError(self, last_line, etype, evalue):
        if etype!=NameError:
            return

        line = last_line
        if len(line.split())==1 and os.path.exists(line):
            if self.automatic_cd and os.path.isdir(line):
                self.report('cd '+line)
                self.smash.shell.magic('pushd '+line)
            else:
                flimit = 712020
                if flimit < os.path.getsize(line):
                    msg = ("warning: maybe you wanted to edit"
                           " that file but it looks big")
                    self.report(msg)
                else:
                    self.report('ed '+line)
                    self.smash.shell.magic('ed '+line)
            return True

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    dwim = DoWhatIMean(ip)
    return dwim

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'
