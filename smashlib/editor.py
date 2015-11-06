""" smashlib.editor
"""

import platform
from smashlib.config import SmashConfig
from smashlib.data import fname_editor_config
def is_osx():
    if platform.mac_ver()[0]:
        # for unix, this returns: ('', ('', '', ''), '')
        return True

def is_windowing_env():
    return is_osx() or is_xwindows() or False

def is_xwindows():
    return os.environ.get('DISPLAY') and \
           'quartz' not in os.environ['DISPLAY']

def get_editor():
    user_editor = None
    c = SmashConfig()
    econfig = c.load_from_etc(fname_editor_config)
    if is_windowing_env:
        user_editor = econfig['window_env']
    else:
        user_editor = econfig['console']
    editor = user_editor
    return editor
