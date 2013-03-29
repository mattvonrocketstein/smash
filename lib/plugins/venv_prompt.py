""" venv_prompt

    Adds the path for the currently activated venv to the main prompt
"""
import os
from threading import Thread
from smashlib.util import do_it_later, truncate_fpath
from smashlib.prompt import prompt, PromptComponent
from smashlib.smash_plugin import SmashPlugin

def this_venv():
    result = os.environ.get('VIRTUAL_ENV','')
    result = truncate_fpath(result)
    result = os.path.sep.join(result.split(os.path.sep)[-2:])
    return '({0})'.format(result)

DEFAULT_SORT_ORDER = 2

class Plugin(SmashPlugin):
    """ Adds the path for the currently activated venv to the main prompt """
    def install(self):
        def adjust_prompt():
            """ there's probably a better way to do this, but
                ipython is not fully initialized when this
                plugin is installed.
            """
            __IPYTHON__._this_venv = this_venv
            t = '''${getattr(__IPYTHON__, '_this_venv', lambda: "")()}'''
            prompt.add(PromptComponent(name='venv_path',
                                       priority=DEFAULT_SORT_ORDER, template=t))
        do_it_later(adjust_prompt, delay=2)
