#!/usr/bin/env python
""" setup.py for smashlib
"""

import os
from setuptools import setup

# __file__ is not set when running from tox
this_dir = os.path.dirname(os.path.abspath(__file__))
if not os.getcwd()==this_dir:
    os.chdir(this_dir)

# make sure we can import the version number so that it doesn't have
# to be changed in two places. smashlib/__init__.py is also free
# to import various requirements that haven't been installed yet
sys.path.append(os.path.join(this_dir, 'smashlib'))
from version import __version__
sys.path.pop()

setup(
    name         = 'smashlib',
    version      = __version__,
    author       = 'mattvonrocketstein',
    author_email = '$author@gmail',
    description  = 'SmaSh: a smart(er) shell',
    url          = 'http://github.com/mattvonrocketstein/smashlib',
    license      = 'MIT',
    keywords     = 'system shell',
    platforms    = 'any',
    zip_safe     = False,
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 000 - Experimental',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent', ],
    packages     = ['smashlib'],
    entry_points = \
    { 'console_scripts': \
      [ 'run_smash = smashlib.bin.smash:entry',
        'pybcompgen = smashlib.bin.pybcompgen:main',
        'pyack = smashlib.bin.pyack:main',
        ]
    }
)
