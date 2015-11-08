""" tests/test_prefilters
"""

from mock import Mock
from smashlib.testing import TestCase, hijack_ipython_module, main
from smashlib.prefilters import url
from smashlib.prefilters import shell

hijack_ipython_module()
from IPython.core.prefilter import PrefilterManager

def fake_line_info(line, **kargs):
    result = Mock()
    result.line = line
    for k, v in kargs.items():
        setattr(result, k, v)
    return result

class TestPrefilterShell(TestCase):
    def setUp(self):
        manager = PrefilterManager()
        self.handler = shell.ShellHandler(prefilter_manager=manager)
        manager._handlers[shell.HANDLER_NAME] = self.handler
        self.checker = shell.ShellChecker(prefilter_manager=manager)

class TestPrefilterURL(TestCase):
    def setUp(self):
        manager = PrefilterManager()
        self.handler = url.URLHandler(prefilter_manager=manager)
        manager._handlers[url.HANDLER_NAME] = self.handler
        self.checker = url.URLChecker(prefilter_manager=manager)

    def test_http_gets_url_handler(self):
        line_info = fake_line_info('http://foo.bar')
        self.assertEqual(
            self.checker.check(line_info),
            self.handler)

    def test_https_gets_url_handler(self):
        line_info = fake_line_info('https://foo.bar')
        self.assertEqual(
            self.checker.check(line_info),
            self.handler)

    def test_random_doesnt_get_url_handler(self):
        line_info = fake_line_info('zoo://foo.bar')
        self.assertEqual(
            self.checker.check(line_info),
            None)

if __name__=='__main__':
    main()
