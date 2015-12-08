""" tests/test_prefilters
"""

from mock import Mock
from smashlib.testing import TestCase, hijack_ipython_module, main
from smashlib.prefilters import url
from smashlib.prefilters import shell

hijack_ipython_module()
from IPython.core.prefilter import PrefilterManager
ia_re = shell.initial_assignments
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

    def test_assignment_prefixes(self):
        self.assertEqual(
            ia_re.match(
                "A_B_C=foo.bar.baz fab create").group(),
            "A_B_C=foo.bar.baz ")
        self.assertEqual(
            ia_re.match('a=b.c fab run:"zoooooooom"').group(),
            'a=b.c '
            )
        self.assertEqual(
            ia_re.match('a="b.c" d="ef" fab create').group(),
            'a="b.c" d="ef" ')

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
