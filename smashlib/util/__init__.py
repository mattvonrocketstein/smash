""" smashlib.util

    Keep imports simple to avoid cycles!
    Safe, simple packages only (no ipython imports in here)
    Stick to stdlib, or known-safe sections of smashlib
"""
import os, re, glob

from smashlib.data import SMASH_ETC, EDITOR_CONFIG_PATH
from goulash.python import get_env, opd, ops, opj, ope, expanduser


def home():
    return get_env('HOME')

def touch_file(_file):
    """ TODO: move to goulash """
    with open(_file, 'w') as handle:
        pass

def require_ipy(require_version):
    import IPython
    ipy_version = IPython.__version__
    if not ipy_version.startswith(require_version):
        err = "smash requires ipython {0}, but your version is {1}"
        raise SystemExit(err.format(require_version, ipy_version))

def guess_dir_type(_dir, max_depth=3):
    """ given a directory and a depth, find which types of
        files are in the directory.  this implementation
        should be reasonably efficient since it won't count
        the number of items or anything.
    """
    type_map = {
        '.py':'python',
        '.pp':'puppet',
        '.md':'docs',
        'Vagrantfile':'vagrant',
        }
    # create a list based on max-depth like ['*', '*/*', '*/*/*', ..]
    globs = [os.path.sep.join(['*']*x) for x in range(1,max_depth+1)]
    matches = []
    for ftype, ftype_name in type_map.items():
        for expr in globs:
            expr = expr + ftype
            if glob.glob(os.path.join(_dir,expr)):
                matches.append(ftype_name)
                break
    return matches

def get_editor():
    import demjson
    from report import report
    from IPython.terminal.interactiveshell import get_default_editor
    _from = None
    user_editor = EDITOR_CONFIG_PATH
    if os.path.exists(user_editor):
        with open(user_editor) as fhandle:
            user_editor = fhandle.read().strip()
        user_editor = [line.strip() for line in user_editor.split('\n')]
        user_editor = filter(lambda x: x and not x.startswith('#'), user_editor)
        err = '{0} should have have 1 line that gives the editor invocation'
        assert len(user_editor)==1, err.format(EDITOR_CONFIG_PATH)
        user_editor = user_editor[0]
        if user_editor:
            print "...found user-specified editor mentioned in "+EDITOR_CONFIG_PATH
    else:
        touch_file(user_editor)
        with open(user_editor,'w') as fhandle:
            fhandle.write("# place editor invocation here (unquoted).\n"
                          "# for example: 'vi' or 'nano --softwrap --quiet'")
        print "... no editor configs are located at '{0}'.".format(user_editor)
        print ".... created an empty template"
        user_editor = None
    sys_editor = get_default_editor()
    editor = user_editor or sys_editor or 'vi'
    print ("...using editor: '{0}'".format(editor))
    return editor

def split_on_unquoted_semicolons(txt):
    # use this in "ed fpath:1:2"?
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]
