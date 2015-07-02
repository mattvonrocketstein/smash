""" tests/sys/test_install.py
"""

import os
import shutil
import tempfile

from unittest import TestCase
from fabric import api

env = os.environ
src_root = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            __file__)))

class TestInstall(TestCase):
    def setUp(self):
        self.tmpd = tempfile.mkdtemp('-smash-sys-test')
        if not hasattr(self, 'original'):
            self.original = os.environ['HOME']
        os.environ['HOME'] = self.tmpd
        self.addCleanup(self._cleanup)
        self.addCleanup(lambda: shutil.rmtree(self.tmpd))
    def _cleanup(self):
        env.__setitem__(
            'HOME', self.original)

    def test_install(self):
        installer = os.path.join(
            src_root,
            'install.py')
        with api.shell_env(HOME=self.tmpd):
            api.local('{0} {1}'.format(
                'python', installer))
            result = api.local(
                '{0} --version'.format(
                    os.path.join(
                        self.tmpd,'bin','smash')),
                capture=True).strip()
            from smashlib.version import __version__ as vinfo
            self.assertEqual(result, str(vinfo))

if __name__=='__main__':
    import unittest
    unittest.main()
