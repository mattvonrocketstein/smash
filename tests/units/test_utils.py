""" tests/test_utils
"""
import os
from smashlib.testing import TestCase, hijack_ipython_module, main
from smashlib.plugins.smash_completer import SmashCompleter, smash_env_complete
from smashlib.overrides import SmashTerminalInteractiveShell
from mock import Mock
hijack_ipython_module()
from IPython.testing.tools import default_config
from IPython.core.completerlib import TryNext
from IPython.testing.globalipapp import get_ipython
from smashlib.util.bash import get_functions_from_file
class TestUtils(TestCase):

    def setUp(self):
        return
        self.shell = Mock()
        self.config = default_config()
        self.shell.config = self.config
        self.plugin = SmashCompleter(self.shell)
        self.event = Mock()

    def test_get_functions_from_file(self):
        ffile = os.path.join(os.path.dirname(__file__),
                             'function.sh')
        self.assertTrue(os.path.exists(ffile))
        self.assertEqual(
            ['simple_function'],
            get_functions_from_file(ffile))


if __name__=='__main__':
    main()
