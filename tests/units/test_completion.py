""" tests/test_completion
"""

from smashlib.testing import TestCase, hijack_ipython_module, main
from smashlib.plugins.smash_completer import SmashCompleter, smash_env_complete
from smashlib.overrides import SmashTerminalInteractiveShell
from mock import Mock
hijack_ipython_module()
from IPython.testing.tools import default_config
from IPython.core.completerlib import TryNext
from IPython.testing.globalipapp import get_ipython

class TestCompletion(TestCase):
    def setUp(self):
        self.shell = Mock()
        self.shell = SmashTerminalInteractiveShell()
        #self.config = default_config()
        #self.shell.config = self.config
        self.plugin = SmashCompleter(self.shell)
        self.event = Mock()


    def test_git(self):
        self.event.line='git clo'
        self.event.text_until_cursor = 'git clo'
        x = self.plugin.smash_matcher(self.shell, self.event)
        from smashlib import embed; embed()
if __name__=='__main__':
    main()
