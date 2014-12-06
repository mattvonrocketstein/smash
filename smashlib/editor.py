""" smashlib.editor
"""

import os
import demjson
import jsonschema

from IPython.terminal.interactiveshell import get_default_editor

from smashlib.data import EDITOR_CONFIG_PATH
from smashlib.util import touch_file

EDITOR_SCHEMA = {
     "type" : "object",
     "properties" : {
         "console" : {"type" : "string"},
         "window_env" : {"type" : "string"},
     },
 }

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
    if os.path.exists(EDITOR_CONFIG_PATH):
        #with open(EDITOR_CONFIG_PATH) as fhandle:
        #    user_editor = fhandle.read().strip()

        try:
            user_editor = demjson.decode_file(EDITOR_CONFIG_PATH)
            jsonschema.validate(user_editor, EDITOR_SCHEMA)
        except demjson.JSONDecodeError:
            print '... warning: found {0} but cannot decode the data'.format(EDITOR_CONFIG_PATH)
        except jsonschema.ValidationError:
            err = ('JSON in {0} does not validate.\n'
                   '\nhere is an example of correct data:\n\n')+\
                   str(get_example(EDITOR_SCHEMA))
            raise SystemExit(err)
        else:
            print "...found editor config in "+EDITOR_CONFIG_PATH
            if is_windowing_env:
                user_editor = user_editor['window_env']
            else:
                user_editor = user_editor['console']
    else:
        touch_file(EDITOR_CONFIG_PATH)
        with open(EDITOR_CONFIG_PATH, 'w') as fhandle:
            fhandle.write(demjson.encode(dict(
                console=sys_editor,
                window_env=sys_editor)))
        print "... no editor configs are located at '{0}'.".format(EDITOR_CONFIG_PATH)
        print ".... created template using {0}".format(sys_editor)
        user_editor = None
    editor = user_editor or sys_editor or 'vi'
    return editor
