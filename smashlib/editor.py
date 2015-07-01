""" smashlib.editor
"""

from smashlib.config import SmashConfig

is_windowing_env = lambda: True  # placeholder


def get_editor():
    user_editor = None
    c = SmashConfig()
    econfig = c.load_from_etc('editor.json')
    if is_windowing_env:
        user_editor = econfig['window_env']
    else:
        user_editor = econfig['console']
    editor = user_editor
    return editor
