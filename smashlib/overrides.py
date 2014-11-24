""" smashlib.overrides

    Things that are not only subclassed from ipython, but intended to
    be used instead of their ipython equivalents.  Similar to
    smashlib.patches, but things in this file are core IPython abstractions.

    So far a lot of this is here mostly because smash wants a separate message
    bus from the main ipython event system (IPython.core.events).
"""

from IPython.terminal.ipapp import TerminalIPythonApp as BaseTIA
from IPython.terminal.interactiveshell import \
     TerminalInteractiveShell as BaseTIS

from smashlib.bin.pybcompgen import complete
from smashlib.pysh import have_command_alias
from smashlib.channels import C_POST_RUN_INPUT, C_POST_RUN_CELL

class SmashTerminalInteractiveShell(BaseTIS):

    def __init__(self,*args,**kargs):
        sooper = super(SmashTerminalInteractiveShell,self)
        sooper.__init__(*args, **kargs)
        self._smash_last_input = ""

    @property
    def smash(self):
        # NOTE: this might not be set during early bootstrap
        return getattr(self, '_smash', None)

    # NOTE: _smash_last_inpute is an accumulator, and input may
    # not be finished.  for example if input is a multi-line
    # function definition, pasted stuff, or uses a trailing "\"
    def raw_input(self, *args, **kargs):
        sooper = super(SmashTerminalInteractiveShell,self)
        out = sooper.raw_input(*args, **kargs)
        self._smash_last_input += out
        return out


    def _showtraceback(self, etype, evalue, stb):
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

        sooper = super(SmashTerminalInteractiveShell, self)
        out = sooper.run_cell(
            raw_cell, store_history=store_history,
            silent=silent, shell_futures=shell_futures)
        if self.smash is not None:
            self.smash.bus.publish(
                C_POST_RUN_CELL,
                self.user_ns['In'][-1].strip())
            self.smash.bus.publish(
                C_POST_RUN_INPUT,
                self._smash_last_input)
            self._smash_last_input = ""
        return out
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
                return complete(line)
            if magic_command_alias:
                return complete(line[1:])
            return []
        self.shell.Completer.matchers = [my_matcher] + \
                                        self.shell.Completer.matchers
TerminalIPythonApp = SmashTerminalIPythonApp
launch_new_instance = TerminalIPythonApp.launch_instance