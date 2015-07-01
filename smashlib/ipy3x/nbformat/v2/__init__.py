"""The main API for the v2 notebook format.

Authors:

* Brian Granger
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

import os

from .nbbase import (
    NotebookNode,
    new_code_cell, new_text_cell, new_notebook, new_output, new_worksheet,
    new_metadata, new_author
)

from .nbjson import reads as reads_json, writes as writes_json
from .nbjson import reads as read_json, writes as write_json
from .nbjson import to_notebook as to_notebook_json

from .nbxml import reads as reads_xml
from .nbxml import reads as read_xml
from .nbxml import to_notebook as to_notebook_xml

from .nbpy import reads as reads_py, writes as writes_py
from .nbpy import reads as read_py, writes as write_py
from .nbpy import to_notebook as to_notebook_py

from .convert import downgrade, upgrade

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------

nbformat = 2
nbformat_minor = 0


def parse_filename(fname):
    """Parse a notebook filename.

    This function takes a notebook filename and returns the notebook
    format (json/py) and the notebook name. This logic can be
    summarized as follows:

    * notebook.ipynb -> (notebook.ipynb, notebook, json)
    * notebook.json  -> (notebook.json, notebook, json)
    * notebook.py    -> (notebook.py, notebook, py)
    * notebook       -> (notebook.ipynb, notebook, json)

    Parameters
    ----------
    fname : unicode
        The notebook filename. The filename can use a specific filename
        extention (.ipynb, .json, .py) or none, in which case .ipynb will
        be assumed.

    Returns
    -------
    (fname, name, format) : (unicode, unicode, unicode)
        The filename, notebook name and format.
    """
    basename, ext = os.path.splitext(fname)
    if ext == u'.ipynb':
        format = u'json'
    elif ext == u'.json':
        format = u'json'
    elif ext == u'.py':
        format = u'py'
    else:
        basename = fname
        fname = fname + u'.ipynb'
        format = u'json'
    return fname, basename, format
