""" smashlib.overrides

    Things that are not only subclassed from ipython, but intended to
    be used instead of their ipython equivalents.  Similar to
    smashlib.patches, but things in this file are core IPython abstractions.

    So far a lot of this is here mostly because smash wants a separate message
    bus from the main ipython event system (IPython.core.events).
"""
import keyword

from IPython.terminal.ipapp import TerminalIPythonApp as BaseTIA
from IPython.terminal.interactiveshell import \
     TerminalInteractiveShell as BaseTIS
from IPython.utils.traitlets import Instance

from smashlib import get_smash
from smashlib.util.ipy import have_command_alias

from smashlib.channels import C_FILE_INPUT
from smashlib.channels import C_POST_RUN_INPUT, C_POST_RUN_CELL, C_COMMAND_FAIL

from smashlib.util import split_on_unquoted_semicolons, is_path
from smashlib.bin.pybcompgen import complete

def smash_bash_complete(*args, **kargs):
    result = complete(*args, **kargs)
    return [ x for x in result if x not in keyword.kwlist ]

class SmashTerminalInteractiveShell(BaseTIS):

    # Input splitter, to transform input line by line and detect when a block
    # is ready to be executed.
    input_splitter = Instance('smashlib.inputsplitter.SmashInputSplitter',
                              (), {'line_input_checker': True})

    def showsyntaxerror(self, filename=None):
        """ when a syntax error is encountered,
            consider just broadcasting a signal instead
            of showing a traceback.
        """
        lastline = self._smash_last_input
        clean_line = lastline.strip()
        if is_path(clean_line):
            self.smash.publish(C_FILE_INPUT, clean_line)
        else:
            sooper = super(SmashTerminalInteractiveShell, self)
            return sooper.showsyntaxerror(filename=filename)


    def __init__(self,*args,**kargs):
        sooper = super(SmashTerminalInteractiveShell, self)
        sooper.__init__(*args, **kargs)
        self._smash_last_input = ""

    @property
    def smash(self):
        # NOTE: this might not be set during early bootstrap
        return getattr(self, '_smash', None)

    # NOTE: _smash_last_input is an accumulator, and input may
    # not be finished.  for example if input is a multi-line
    # function definition, pasted stuff, or uses a trailing "\"
    def raw_input(self, *args, **kargs):
        sooper = super(SmashTerminalInteractiveShell,self)
        out = sooper.raw_input(*args, **kargs)
        self._smash_last_input += out
        return out


    def _showtraceback(self, etype, evalue, stb):
        """ before we display the traceback, give smash error
            handlers one more chance to do something smart """
        sooper = super(SmashTerminalInteractiveShell, self)
        if self.smash is not None:
            for handler in self.smash.error_handlers:
                handled = handler(
                    self._smash_last_input, etype, evalue)
                if handled:
                    return
        return sooper._showtraceback(etype,evalue,stb)

    # NOTE: when run-cell runs, input is finished
    def run_cell(self, raw_cell, store_history=False,
                 silent=False, shell_futures=True):

        # as long as the expressions are semicolon separated,
        # this section allows hybrid bash/python expressions
        bits = split_on_unquoted_semicolons(raw_cell)
        if len(bits) > 1:
            out=[]
            for x in bits:
                out.append(
                    self.run_cell(
                        x, store_history=store_history,
                        silent=silent, shell_futures=shell_futures))
            return out

        sooper = super(SmashTerminalInteractiveShell, self)
        out = sooper.run_cell(
            raw_cell, store_history=store_history,
            silent=silent, shell_futures=shell_futures)
        if self.smash is not None:
            if self._smash_last_input:
                # translated-input
                this = self.user_ns['In'][-1].strip()
                # untranslated-input
                last_input=self._smash_last_input
                self.smash.publish(C_POST_RUN_CELL, this)
                self.smash.publish(C_POST_RUN_INPUT, last_input)
            self._smash_last_input = ""
        return out

    def system(self, cmd, quiet=False, **kargs):
        #print 'wrapping system call',cmd
        result = super(SmashTerminalInteractiveShell,self).system(cmd,**kargs)
        error = self.user_ns['_exit_code'] # put exit code into bash for lp?s
        if error:
            get_smash().publish(C_COMMAND_FAIL, cmd, error)
        if not quiet and result:
            print result
TerminalInteractiveShell=SmashTerminalInteractiveShell


class SmashTerminalIPythonApp(BaseTIA):
    @classmethod
    def launch_instance(cls, argv=None, **kwargs):
        app = cls.instance(**kwargs)
        app.initialize(argv)
        app.start()

    def init_shell(self):
        """function override so we can use SmashTerminalInteractiveShell """
        self.shell = TerminalInteractiveShell.instance(
            parent=self, display_banner=False,
            profile_dir=self.profile_dir,
            ipython_dir=self.ipython_dir,
            user_ns=self.user_ns)
        self.shell.configurables.append(self)
        def my_matcher(text):
            line = self.shell.Completer.readline.get_line_buffer()
            first_word = line.split()[0]
            magic_command_alias = first_word.startswith('%') and \
                                  have_command_alias(first_word[1:])
            naked_command_alias = have_command_alias(first_word)
            if naked_command_alias:
                return smash_bash_complete(line)
            if magic_command_alias:
                return smash_bash_complete(line[1:])
            return []
        self.shell.Completer.matchers = [my_matcher] + \
                                        self.shell.Completer.matchers
TerminalIPythonApp = SmashTerminalIPythonApp
launch_new_instance = TerminalIPythonApp.launch_instance
