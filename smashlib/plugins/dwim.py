""" smashlib.plugins.dwim

    documentation: http://mattvonrocketstein.github.io/smash/plugins.html#dwim
"""
from IPython.utils.traitlets import Bool
from IPython.utils.traitlets import EventfulDict

from smashlib.v2 import Reporter
from smashlib.util.events import receives_event
from smashlib.channels import C_FILE_INPUT, C_URL_INPUT
from smashlib.util._fabric import qlocal
from smashlib.util._fabric import has_bin

from goulash.python import splitext, ope, abspath, expanduser, isdir
import webbrowser


def is_editable(_fpath):
    """ guess whether _fpath can be edited, based on
        the output of the file(1) utility.  this function
        refuses to guess if file(1) is not available.

        FIXME: check if its small
    """
    # flimit = 712020
    # if flimit < os.path.getsize(line):
    #   msg = ("warning: maybe you wanted to edit"
    #          " that file but it looks big")
    #   self.report(msg)
    if has_bin('file'):
        file_result = qlocal('file {0}'.format(_fpath), capture=True).strip()
        if 'ASCII text' in file_result or file_result.endswith('empty'):
            return True
        else:
            return False

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

    @receives_event(C_URL_INPUT)
    def on_url_input(self, fpath):
        webbrowser.open(fpath)
        self.report("opening input in browser")

    @receives_event(C_FILE_INPUT)
    def on_file_input(self, fpath):
        def doit(_fpath, _suffix, _opener, _rest):
            if ope(_fpath) and not isdir(_fpath):
                if _opener is not None:
                    self.report('Using _opener "{0}" for "{1}"'.format(_opener, _suffix))
                    return '{0} {1}'.format(_opener, _fpath+_rest)
                else:
                    msg = "Legit file input, but no _suffix alias could be found for "+_suffix
                    self.report(msg)
                    if is_editable(_fpath):
                        self.report("File looks like ASCII text, assuming I should edit it")
                        return doit(_fpath, _suffix, 'ed', _rest)
            else:
                msg = 'Attempted file input, but path "{0}" does not exist'.format(fpath)
                self.report(msg)

        fpath = abspath(expanduser(fpath))

        #isolate file:col:row syntax
        if not ope(fpath) and ':' in fpath:
            tmp = fpath
            fpath = tmp[:tmp.find(':')]
            rest = tmp[tmp.find(':'):]
        else:
            rest = ''

        #isolate file suffix, guess an opener
        suffix = splitext(fpath)[-1][1:].lower()
        opener = self.suffix_aliases.get(suffix, None)
        if isdir(fpath) and self.automatic_cd:
            self.report('cd '+fpath)
            self.smash.shell.magic('pushd '+fpath)
            return True

        cmd = doit(fpath, suffix, opener, rest)
        if cmd:
            self.smash.shell.run_cell(cmd)
            return True

    def init(self):
        #def smash_open(x):
        #    webbrowser.open(x)
        #self.contribute_magic(smash_open)
        if self.automatic_cd or self.automatic_edit:
            self.smash.error_handlers.append(self.handle_NameError)

    def handle_NameError(self, last_line, etype, evalue):
        if etype != NameError:
            return
        line = last_line
        return self.on_file_input('fake_bus', last_line)


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    dwim = DoWhatIMean(ip)
    return dwim

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'
