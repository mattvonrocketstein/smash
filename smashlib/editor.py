""" smashlib.editor
"""

import os
import demjson
import jsonschema

from IPython.terminal.interactiveshell import get_default_editor

from smashlib.data import EDITOR_CONFIG_PATH
from smashlib.util import touch_file
from smashlib.config import SmashConfig
#from smashlib.config.schemas import EDITOR_SCHEMA

#def validate(data, schema):

def get_example(schema):
    props = [x for x in schema['properties']]
    out={}
    for p in props:
        typ=schema['properties'][p]['type']
        if typ=='string':
            out[p] = 'foo'
        else:
            raise Exception('niy')
    return str(out)

def get_editor():
    user_editor = None
    sys_editor = get_default_editor()
    is_windowing_env = lambda: True # placeholder

    c = SmashConfig()
    econfig = c.load_from_etc('editor.json')
    if is_windowing_env:
        user_editor = econfig['window_env']
    else:
        user_editor = econfig['console']
    editor = user_editor or sys_editor or 'vi'
    return editor
