""" ipython_hacks/ipy_venv_support

    This file mainly exists to make virtual-env's work better with
    the pysh profile.  To use, first move this file into ~/.ipython.

    After that, you invoke in one of two ways.

      1) in pure python

        >>> from ipy_venv_support import activate_venv
        >>> activate_venv('/path/to/venv')
        => activate_this.py ..
        => VIRTUAL_ENV=/home/matt/code/hammock/node
        => Rehashing shell aliases to include /home/matt/code/hammock/node/bin

      2) as a magic command (not finished yet)

        ...
        ...
        ...
"""
import os

def activate_venv(path):
    """ programmatically activate virtualenv.

        see also: http://pypi.python.org/pypi/virtualenv
    """
    if 'VIRTUAL_ENV' in os.environ:
        if os.environ['VIRTUAL_ENV']==path:
            return
        else:
            raise ValueError, "VIRTUAL_ENV already set to"+os.environ['VIRTUAL_ENV']

    assert os.path.exists(path)

    def choose_dir(path):
        if 'activate_this.py' in os.listdir(path):
            return path
        node_bin   = os.path.join(path, 'node', 'bin', 'activate_this.py')
        simple_bin = os.path.join(path, 'bin', 'activate_this.py')
        if os.path.exists(node_bin):
            return node_bin
        if os.path.exists(simple_bin):
            return simple_bin
        err = "Cannot activate venv: none of these are present- {tries}"
        tries = [path, simple_bin, node_bin]
        raise Exception, err.format(tries=tries)

    # make python ready
    print '  => activate_this.py ..'
    activate_this = choose_dir(path)
    execfile(activate_this, dict(__file__=activate_this))

    # for consistency
    venv = os.path.split(os.path.split(activate_this)[0])[0]
    os.environ['VIRTUAL_ENV'] = venv
    print '  => VIRTUAL_ENV={venv}'.format(venv=os.environ['VIRTUAL_ENV'])

    # great, but now we still don't get the usual access to the venv's bin
    bindir = os.path.join(venv,'bin')
    os.environ['PATH'] = bindir+':'+os.environ['PATH']
    print '  => Rehashing shell aliases to include', bindir
    __IPYTHON__.ipmagic('rehashx')
    __IPYTHON__.ipmagic('cd ' + venv)
