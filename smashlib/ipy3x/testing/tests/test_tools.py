# encoding: utf-8
"""
Tests for testing.tools
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import with_statement
from __future__ import print_function

import os
import unittest

import nose.tools as nt

from IPython.testing import decorators as dec
from IPython.testing import tools as tt

#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------


@dec.skip_win32
def test_full_path_posix():
    spath = '/foo/bar.py'
    result = tt.full_path(spath, ['a.txt', 'b.txt'])
    nt.assert_equal(result, ['/foo/a.txt', '/foo/b.txt'])
    spath = '/foo'
    result = tt.full_path(spath, ['a.txt', 'b.txt'])
    nt.assert_equal(result, ['/a.txt', '/b.txt'])
    result = tt.full_path(spath, 'a.txt')
    nt.assert_equal(result, ['/a.txt'])


@dec.skip_if_not_win32
def test_full_path_win32():
    spath = 'c:\\foo\\bar.py'
    result = tt.full_path(spath, ['a.txt', 'b.txt'])
    nt.assert_equal(result, ['c:\\foo\\a.txt', 'c:\\foo\\b.txt'])
    spath = 'c:\\foo'
    result = tt.full_path(spath, ['a.txt', 'b.txt'])
    nt.assert_equal(result, ['c:\\a.txt', 'c:\\b.txt'])
    result = tt.full_path(spath, 'a.txt')
    nt.assert_equal(result, ['c:\\a.txt'])


def test_parser():
    err = ("FAILED (errors=1)", 1, 0)
    fail = ("FAILED (failures=1)", 0, 1)
    both = ("FAILED (errors=1, failures=1)", 1, 1)
    for txt, nerr, nfail in [err, fail, both]:
        nerr1, nfail1 = tt.parse_test_output(txt)
        nt.assert_equal(nerr, nerr1)
        nt.assert_equal(nfail, nfail1)


def test_temp_pyfile():
    src = 'pass\n'
    fname, fh = tt.temp_pyfile(src)
    assert os.path.isfile(fname)
    fh.close()
    with open(fname) as fh2:
        src2 = fh2.read()
    nt.assert_equal(src2, src)


class TestAssertPrints(unittest.TestCase):

    def test_passing(self):
        with tt.AssertPrints("abc"):
            print("abcd")
            print("def")
            print(b"ghi")

    def test_failing(self):
        def func():
            with tt.AssertPrints("abc"):
                print("acd")
                print("def")
                print(b"ghi")

        self.assertRaises(AssertionError, func)


class Test_ipexec_validate(unittest.TestCase, tt.TempFileMixin):

    def test_main_path(self):
        """Test with only stdout results.
        """
        self.mktmp("print('A')\n"
                   "print('B')\n"
                   )
        out = "A\nB"
        tt.ipexec_validate(self.fname, out)

    def test_main_path2(self):
        """Test with only stdout results, expecting windows line endings.
        """
        self.mktmp("print('A')\n"
                   "print('B')\n"
                   )
        out = "A\r\nB"
        tt.ipexec_validate(self.fname, out)

    def test_exception_path(self):
        """Test exception path in exception_validate.
        """
        self.mktmp("from __future__ import print_function\n"
                   "import sys\n"
                   "print('A')\n"
                   "print('B')\n"
                   "print('C', file=sys.stderr)\n"
                   "print('D', file=sys.stderr)\n"
                   )
        out = "A\nB"
        tt.ipexec_validate(self.fname, expected_out=out, expected_err="C\nD")

    def test_exception_path2(self):
        """Test exception path in exception_validate, expecting windows line endings.
        """
        self.mktmp("from __future__ import print_function\n"
                   "import sys\n"
                   "print('A')\n"
                   "print('B')\n"
                   "print('C', file=sys.stderr)\n"
                   "print('D', file=sys.stderr)\n"
                   )
        out = "A\r\nB"
        tt.ipexec_validate(self.fname, expected_out=out, expected_err="C\r\nD")