
import re
import nose.tools as nt

from IPython.html.base.handlers import path_regex, notebook_path_regex

try: # py3
    assert_regex = nt.assert_regex
    assert_not_regex = nt.assert_not_regex
except AttributeError: # py2
    assert_regex = nt.assert_regexp_matches
    assert_not_regex = nt.assert_not_regexp_matches


# build regexps that tornado uses:
path_pat = re.compile('^' + '/x%s' % path_regex + '$')
nb_path_pat = re.compile('^' + '/y%s' % notebook_path_regex + '$')

def test_path_regex():
    for path in (
        '/x',
        '/x/',
        '/x/foo',
        '/x/foo.ipynb',
        '/x/foo/bar',
        '/x/foo/bar.txt',
    ):
        assert_regex(path, path_pat)

def test_path_regex_bad():
    for path in (
        '/xfoo',
        '/xfoo/',
        '/xfoo/bar',
        '/xfoo/bar/',
        '/x/foo/bar/',
        '/x//foo',
        '/y',
        '/y/x/foo',
    ):
        assert_not_regex(path, path_pat)

def test_notebook_path_regex():
    for path in (
        '/y/asdf.ipynb',
        '/y/foo/bar.ipynb',
        '/y/a/b/c/d/e.ipynb',
    ):
        assert_regex(path, nb_path_pat)

def test_notebook_path_regex_bad():
    for path in (
        '/y',
        '/y/',
        '/y/.ipynb',
        '/y/foo/.ipynb',
        '/y/foo/bar',
        '/yfoo.ipynb',
        '/yfoo/bar.ipynb',
    ):
        assert_not_regex(path, nb_path_pat)
