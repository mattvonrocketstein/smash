""" smashlib.completion
"""

import re
import sys
import subprocess
import itertools
from smashlib._logging import smash_log, completion_log
from smashlib.util.ipy import have_command_alias
from smashlib.ipy3x.core.completer import IPCompleter as IPCompleter
from smashlib.ipy3x.core.completer import penalize_magics_key, Bunch

from IPython.core.error import TryNext
from IPython.utils.py3compat import PY3, builtin_mod

USELESS_BUILTINS = 'credits copyright'.split()


def complete_long_opts(cmd):
    """ completes long-opts args for any command,
        assuming it supports --help
    """
    tmp = subprocess.check_output(cmd + ' --help', shell=True)
    out = re.compile('\s+--[a-zA-Z]+').findall(tmp)
    out += re.compile('\s+-[a-zA-Z]+').findall(tmp)
    out = [x.strip() for x in out]
    out = list(set(out))
    return out


class opt_completer(object):

    """ """

    def __init__(self, cmd_name):
        self.cmd = cmd_name

    def __call__(self, himself, event):
        if event.symbol in ['-', '--']:
            return complete_long_opts(self.cmd)
        return []

USELESS_NAMESPACE = 'credits copyright'.split()


class SmashCompleter(IPCompleter):

    # unmodified from IPython's original method, here for
    # convenience in case debugging messages are needed
    def dispatch_custom_completer(self, text):
        # io.rprint("Custom! '%s' %s" % (text, self.custom_completers)) # dbg
        line = self.line_buffer
        if not line.strip():
            return None

        # Create a little structure to pass all the relevant information about
        # the current completion to any custom completer.
        event = Bunch()
        event.line = line
        event.symbol = text
        cmd = line.split(None, 1)[0]
        event.command = cmd
        event.text_until_cursor = self.text_until_cursor

        # print "\ncustom:{%s]\n" % event # dbg

        # for foo etc, try also to find completer for %foo
        if not cmd.startswith(self.magic_escape):
            try_magic = self.custom_completers.s_matches(
                self.magic_escape + cmd)
        else:
            try_magic = []

        for c in itertools.chain(
                self.custom_completers.s_matches(cmd),
                try_magic,
                self.custom_completers.flat_matches(self.text_until_cursor)):
            # print "try",c # dbg
            try:
                res = c(event)
                if res:
                    # first, try case sensitive match
                    withcase = [r for r in res if r.startswith(text)]
                    if withcase:
                        return withcase
                    # if none, then case insensitive ones are ok too
                    text_low = text.lower()
                    return [r for r in res if r.lower().startswith(text_low)]
            except TryNext:
                pass
        return None

    # almost unmodified from ipython original, but changed to
    # avoid completion over ALL the many builtins.
    COMPLETE_BUILTINS = list(
        set(builtin_mod.__dict__.keys()) -
        set(USELESS_BUILTINS))

    def global_matches(self, text):
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in functions and names currently
        defined in self.namespace or self.global_namespace that match.

        """
        # print 'Completer->global_matches, txt=%r' % text # dbg
        matches = []
        match_append = matches.append
        n = len(text)

        for lst in [keyword.kwlist,
                    COMPLETE_BUILTINS,
                    self.namespace.keys(),
                    self.global_namespace.keys()]:
            for word in lst:
                if word[:n] == text and word != "__builtins__":
                    match_append(word)
        return matches

    def complete(self, text=None, line_buffer=None, cursor_pos=None):
        completion_log.info("received data: [{0}]".format(
            [text, line_buffer, cursor_pos]))
        """Find completions for the given text and line context.

        Note that both the text and the line_buffer are optional, but at least
        one of them must be given.

        Parameters
        ----------
          text : string, optional
            Text to perform the completion on.  If not given, the line buffer
            is split using the instance's CompletionSplitter object.

          line_buffer : string, optional
            If not given, the completer attempts to obtain the current line
            buffer via readline.  This keyword allows clients which are
            requesting for text completions in non-readline contexts to inform
            the completer of the entire text.

          cursor_pos : int, optional
            Index of the cursor in the full line buffer.  Should be provided by
            remote frontends where kernel has no access to frontend state.

        Returns
        -------
        text : str
          Text that was actually used in the completion.

        matches : list
          A list of completion matches.
        """
        # io.rprint('\nCOMP1 %r %r %r' % (text, line_buffer, cursor_pos))  #
        # dbg

        # if the cursor position isn't given, the only sane assumption we can
        # make is that it's at the end of the line (the common case)
        if cursor_pos is None:
            cursor_pos = len(line_buffer) if text is None else len(text)

        if PY3:
            latex_text = text if not line_buffer else line_buffer[:cursor_pos]
            latex_text, latex_matches = self.latex_matches(latex_text)
            if latex_matches:
                return latex_text, latex_matches

        # if text is either None or an empty string, rely on the line buffer
        if not text:
            text = self.splitter.split_line(line_buffer, cursor_pos)

        # If no line buffer is given, assume the input text is all there was
        if line_buffer is None:
            line_buffer = text

        self.line_buffer = line_buffer
        self.text_until_cursor = self.line_buffer[:cursor_pos]
        # io.rprint('COMP2 %r %r %r' % (text, line_buffer, cursor_pos))  # dbg

        # Start with a clean slate of completions
        self.matches[:] = []
        custom_res = self.dispatch_custom_completer(text)
        if custom_res is not None:
            # did custom completers produce something?
            completion_log.info("custom completers: {0}".format(custom_res))
            self.matches = custom_res
        else:
            # Extend the list of completions with the results of each
            # matcher, so we return results to the user from all
            # namespaces.
            if self.merge_completions:
                self.matches = []
                for matcher in self.matchers:
                    extra = matcher(text)
                    self.matches.extend(extra)
                    completion_log.info(
                        "extending matches with: {0}".format(extra))
                    # try:
                    #    self.matches.extend(matcher(text))
                    # except:
                    # Show the ugly traceback if the matcher causes an
                    # exception, but do NOT crash the kernel!
                    #    raise
                    #   sys.excepthook(*sys.exc_info())
            else:
                for matcher in self.matchers:
                    self.matches = matcher(text)
                    if self.matches:
                        completion_log.info(
                            "returning matches from: {0}".format(matcher))
                        break
        # FIXME: we should extend our api to return a dict with completions for
        # different types of objects.  The rlcomplete() method could then
        # simply collapse the dict into a list for readline, but we'd have
        # richer completion semantics in other evironments.

        # use penalize_magics_key to put magics after variables with same name
        self.matches = sorted(set(self.matches), key=penalize_magics_key)

        completion_log.info('COMP TEXT, MATCHES: %r, %r' %
                            (text, self.matches))  # dbg
        return text, self.matches

    def magic_matches(self, text):
        completion_log.debug("completing [{0}]".format(text))
        # print 'Completer->magic_matches:',text,'lb',self.text_until_cursor # dbg
        # Get all shell magics now rather than statically, so magics loaded at
        # runtime show up too.
        lsm = self.shell.magics_manager.lsmagic()
        line_magics = lsm['line']
        cell_magics = lsm['cell']
        pre = self.magic_escape
        pre2 = pre + pre

        # Completion logic:
        # - user gives %%: only do cell magics
        # - user gives %: do both line and cell magics
        # - no prefix: do both
        # In other words, line magics are skipped if the user gives %%
        # explicitly
        bare_text = text.lstrip(pre)
        comp = [pre2 + m for m in cell_magics if m.startswith(bare_text)]
        if not text.startswith(pre2):
            comp += [pre + m for m in line_magics if m.startswith(bare_text)]
            # do not allow known shell commands to be prefixed
            # with '%' as if they were magic commands
            for i, x in enumerate(comp):
                original = x[len(pre):]
                if have_command_alias(original):
                    comp[i] = original
        return comp
