""" smashlib.overrides

    Things that are not only subclassed from ipython, but intended to
    be used instead of their ipython equivalents.  Similar to
    smashlib.patches, but things in this file are core IPython abstractions.

    So far a lot of this is here mostly because smash wants a separate message
    bus from the main ipython event system (IPython.core.events).
"""
import traceback
from report import report, console

from IPython.terminal.ipapp import TerminalIPythonApp as BaseTIA
from IPython.terminal.interactiveshell import \
    TerminalInteractiveShell as BaseTIS
from IPython.utils.traitlets import Instance, Type
from IPython.core.displayhook import DisplayHook
from IPython.utils.strdispatch import StrDispatch
from IPython.core.completerlib import (
    module_completer, magic_run_completer,
    cd_completer, reset_completer)
from IPython.core import page

from smashlib._logging import smash_log
from smashlib.channels import C_FILE_INPUT, C_PRE_RUN_CELL
from smashlib.channels import C_POST_RUN_INPUT, C_POST_RUN_CELL
from smashlib.util import split_on_unquoted_semicolons, is_path
from smashlib.completion import SmashCompleter


class SmashDisplayHook(DisplayHook):

    def finish_displayhook(self):
        """Finish up all displayhook activities."""
        try:
            super(SmashDisplayHook, self).finish_displayhook()
        except AttributeError, e:
            # occasionally throws
            # IOStream instance has no attribute 'flush'
            #
            # I think this is a race condition on embedded shells
            report(str(e))


class SmashTerminalInteractiveShell(BaseTIS):

    # Input splitter, to transform input line by line and detect when a block
    # is ready to be executed.
    input_splitter = Instance('smashlib.inputsplitter.SmashInputSplitter',
                              (), {'line_input_checker': True})
    displayhook_class = Type(SmashDisplayHook)

    def show_usage(self):
        """ handler used when naked '?' is entered into the terminal """
        return page.page(
            console.red("main documentation:") + \
            "\n  http://mattvonrocketstein.github.io/smash/")

    def showsyntaxerror(self, filename=None):
        """ when a syntax error is encountered,
            consider just broadcasting a signal instead
            of showing a traceback.
        """
        smash_log.info(
            "last efforts to do something "
            "meaningful with input before "
            "syntax error")
        lastline = self._smash_last_input
        clean_line = lastline.strip()
        if not clean_line:
            # this is not input!
            # possibly there is actually an error in smash itself
            raise

        if is_path(clean_line):
            # NB: in this case a regex looks like a path or URL,
            # but it's not necessarily true that the endpoint
            # actuals exists
            self.smash.publish(C_FILE_INPUT, clean_line)
        elif is_path(clean_line.split()[0]):
            self.system(clean_line)
        else:
            smash_log.info('nothing to do but call super()')
            sooper = super(SmashTerminalInteractiveShell, self)
            return sooper.showsyntaxerror(filename=filename)

    def __init__(self, *args, **kargs):
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
        sooper = super(SmashTerminalInteractiveShell, self)
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
        if etype == NameError:
            if len(self._smash_last_input.split('\n')) == 1:
                msg = 'smash: {0}: command not found'
                msg = msg.format(
                    self._smash_last_input.strip())
                print msg
                return
        else:
            return sooper._showtraceback(etype, evalue, stb)

    # NOTE: when run-cell runs, input is finished
    def run_cell(self, raw_cell, store_history=False,
                 silent=False, shell_futures=True):
        #assert self.smash
        #import re
        #regex = r'`[^`]*`';
        #line ='foo`bar`baz`a`';
        #tick_groups = [x[1:-1] for x in re.findall(regex, line)];
        #if tick_groups:
        #    print tick_groups

        #avoid race on embedded shell
        publish = getattr(self.smash,'publish',None)
        if publish:
            publish(C_PRE_RUN_CELL, raw_cell)
        smash_log.info("[{0}]".format(raw_cell.encode('utf-8').strip()))
        # as long as the expressions are semicolon separated,
        # this section allows hybrid bash/python expressions
        bits = split_on_unquoted_semicolons(raw_cell)
        if len(bits) > 1:
            smash_log.info("detected chaining with this input")
            out = []
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
                last_input = self._smash_last_input
                self.smash.publish(C_POST_RUN_CELL, this)
                self.smash.publish(C_POST_RUN_INPUT, last_input)
            self._smash_last_input = ""
        return [out]

    def ask_exit(self):
        """ """
        self.smash.scheduler.stop()
        super(SmashTerminalInteractiveShell, self).ask_exit()

    def system(self, cmd, quiet=False, **kargs):
        # print 'wrapping system call',cmd
        result = super(SmashTerminalInteractiveShell, self).system(
            cmd, **kargs)
        # put exit code into os.environ?
        error = self.user_ns['_exit_code']
        smash_log.info("exit code: {0}".format(error))
        # if error:
        #    get_smash().publish(C_COMMAND_FAIL, cmd, error)
        if not quiet and result:
            print result

    def init_completer(self):
        #
        # copied for modification from smashlib.ipy3x.core.interactiveshell
        #
        self.Completer = SmashCompleter(
            shell=self,
            namespace=self.user_ns,
            global_namespace=self.user_global_ns,
            use_readline=self.has_readline,
            parent=self,)

        self.configurables.append(self.Completer)

        # Add custom completers to the basic ones built into IPCompleter
        sdisp = self.strdispatchers.get('complete_command', StrDispatch())
        self.strdispatchers['complete_command'] = sdisp
        self.Completer.custom_completers = sdisp

        self.set_hook('complete_command', module_completer, str_key='import')
        self.set_hook('complete_command', module_completer, str_key='from')
        self.set_hook('complete_command', magic_run_completer, str_key='%run')
        self.set_hook('complete_command', cd_completer, str_key='%cd')
        self.set_hook('complete_command', reset_completer, str_key='%reset')

        # Only configure readline if we truly are using readline.  IPython can
        # do tab-completion over the network, in GUIs, etc, where readline
        # itself may be absent
        if self.has_readline:
            self.set_readline_completer()

TerminalInteractiveShell = SmashTerminalInteractiveShell


class SmashTerminalIPythonApp(BaseTIA):
    def init_extensions(self):
        try:
            self.log.info("Loading IPython extensions...")
            extensions = self.default_extensions + self.extensions
            for ext in extensions:
                try:
                    self.log.info(
                        "Loading IPython extension into Smash: %s" % ext)
                    self.shell.extension_manager.load_extension(ext)
                except:
                    msg = ("Error in loading extension: {0}"
                           "\nCheck your config files in %s")
                    msg = msg.format(ext, self.profile_dir.location)
                    self.log.warn(msg)
                    smash_log.critical(traceback.format_exc())
                    self.shell.showtraceback()
        except:
            self.log.info("Unknown error in loading extensions:")
            self.shell.showtraceback()

    @classmethod
    def launch_instance(cls, argv=None, **kwargs):
        app = cls.instance(**kwargs)
        app.initialize(argv)
        app.start()

    def init_shell(self):
        """ function override so we can use SmashTerminalInteractiveShell """
        self.shell = TerminalInteractiveShell.instance(
            parent=self, display_banner=False,
            profile_dir=self.profile_dir,
            ipython_dir=self.ipython_dir,
            user_ns=self.user_ns)
        self.shell.configurables.append(self)

TerminalIPythonApp = SmashTerminalIPythonApp
launch_new_instance = TerminalIPythonApp.launch_instance
