#!/usr/bin/env python
#
# fabfile for smashlib
#
# this file is a self-hosting fabfile, meaning it
# supports direct invocation with standard option
# parsing, including --help and -l (for listing commands).
#
# summary of commands/arguments:
#
#   * fab pypi_repackage: update this package on pypi
#   * fab version_bump: increase package version by $VERSION_DELTA
#
import os, re, sys

from fabric.api import env, run
from fabric.colors import red
from fabric.api import lcd, local, quiet, settings
from fabric.contrib.console import confirm
from fabric.colors import red

VERSION_DELTA = .01

_ope = os.path.exists
_mkdir = os.mkdir
_expanduser = os.path.expanduser
_dirname = os.path.dirname

ldir = _dirname(__file__)

def version_bump():
    """ bump the version number """
    sandbox = {}
    version_file = os.path.join('smashlib', 'version.py')
    err = 'version file not found in expected location: ' + version_file
    assert os.path.exists(version_file), err
    execfile(version_file, sandbox)
    current_version = sandbox['__version__']
    new_version = current_version + VERSION_DELTA
    with open(version_file, 'r') as fhandle:
        version_file_contents = [x for x in fhandle.readlines() if x.strip()]
    new_file = version_file_contents[:-1]+["__version__={0}".format(new_version)]
    new_file = '\n'.join(new_file)
    print red("warning:") + " version will be changed to {0}".format(new_version)
    print
    print red("new version file will look like this:\n")
    print new_file
    ans = confirm('proceed with version change?'.format(ldir))
    if not ans:
        print 'aborting.'
        return
    with open(version_file,'w') as fhandle:
        fhandle.write(new_file)
        print 'version has been rewritten.'

def pypi_repackage():
    """ refreshes the pypi bundle for this project """
    print red("warning:") + (" by now you should have commited local"
                             " master and bumped version string")
    ans = confirm('proceed with pypi update in "{0}"?'.format(ldir))
    if not ans: return
    with lcd(ldir):
        local("git checkout -b pypi") # in case this has never been done before
        with settings(warn_only=True):
            local("git checkout -b pypi") # in case this has never been done before
        local("git reset --hard master")
        local("python setup.py register -r pypi")
        local("python setup.py sdist upload -r pypi")

if __name__ == '__main__':
    # a neat hack that makes this file a "self-hosting" fabfile,
    # ie it is invoked directly but still gets all the fabric niceties
    # like real option parsing, including --help and -l (for listing
    # commands). note that as of fabric 1.10, the file for some reason
    # needs to end in .py, despite what the documentation says.  see:
    # http://docs.fabfile.org/en/1.4.2/usage/fabfiles.html#fabfile-discovery
    #
    # the .index() manipulation below should make this work regardless of
    # whether this is invoked from shell as "./foo.py" or "python foo.py"
    import sys
    from fabric.main import main as fmain
    patched_argv = ['fab', '-f', __file__,] + \
                   sys.argv[sys.argv.index(__file__)+1:]
    sys.argv = patched_argv
    fmain()
