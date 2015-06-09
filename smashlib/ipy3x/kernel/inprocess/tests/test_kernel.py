# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import sys
import unittest

from IPython.kernel.inprocess.blocking import BlockingInProcessKernelClient
from IPython.kernel.inprocess.manager import InProcessKernelManager
from IPython.kernel.inprocess.ipkernel import InProcessKernel
from IPython.testing.decorators import skipif_not_matplotlib
from IPython.utils.io import capture_output
from IPython.utils import py3compat

if py3compat.PY3:
    from io import StringIO
else:
    from StringIO import StringIO


class InProcessKernelTestCase(unittest.TestCase):

    def setUp(self):
        self.km = InProcessKernelManager()
        self.km.start_kernel()
        self.kc = BlockingInProcessKernelClient(kernel=self.km.kernel)
        self.kc.start_channels()

    @skipif_not_matplotlib
    def test_pylab(self):
        """Does %pylab work in the in-process kernel?"""
        kc = self.kc
        kc.execute('%pylab')
        msg = get_stream_message(kc)
        self.assertIn('matplotlib', msg['content']['text'])

    def test_raw_input(self):
        """ Does the in-process kernel handle raw_input correctly?
        """
        io = StringIO('foobar\n')
        sys_stdin = sys.stdin
        sys.stdin = io
        try:
            if py3compat.PY3:
                self.kc.execute('x = input()')
            else:
                self.kc.execute('x = raw_input()')
        finally:
            sys.stdin = sys_stdin
        self.assertEqual(self.km.kernel.shell.user_ns.get('x'), 'foobar')

    def test_stdout(self):
        """ Does the in-process kernel correctly capture IO?
        """
        kernel = InProcessKernel()

        with capture_output() as io:
            kernel.shell.run_cell('print("foo")')
        self.assertEqual(io.stdout, 'foo\n')

        kc = BlockingInProcessKernelClient(kernel=kernel)
        kernel.frontends.append(kc)
        kc.shell_channel.execute('print("bar")')
        msg = get_stream_message(kc)
        self.assertEqual(msg['content']['text'], 'bar\n')

#-----------------------------------------------------------------------------
# Utility functions
#-----------------------------------------------------------------------------

def get_stream_message(kernel_client, timeout=5):
    """ Gets a single stream message synchronously from the sub channel.
    """
    while True:
        msg = kernel_client.get_iopub_msg(timeout=timeout)
        if msg['header']['msg_type'] == 'stream':
            return msg


if __name__ == '__main__':
    unittest.main()
