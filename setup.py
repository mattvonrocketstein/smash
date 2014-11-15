#!/usr/bin/env python
""" setup.py for smashlib
"""

import os
from setuptools import setup
this_dir = os.path.dirname(__file__)
if not os.getcwd()==this_dir:
    os.chdir(this_dir)
setup(
    name         = 'smashlib',
    author       = 'mattvonrocketstein',
    author_email = '$author@gmail',
    version      = '0.1',
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
