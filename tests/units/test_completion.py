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
        self.config = default_config()
        self.shell.config = self.config
        self.plugin = SmashCompleter(self.shell)
        self.event = Mock()

if __name__=='__main__':
    main()
