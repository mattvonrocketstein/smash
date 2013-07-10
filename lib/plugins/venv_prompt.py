""" venv_prompt

    Adds the path for the currently activated venv to the main prompt
"""
import os
from threading import Thread
from smashlib.util import do_it_later, truncate_fpath
from smashlib.prompt import prompt, PromptComponent, showVenv
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import this_venv

class PromptPlugin(SmashPlugin):
    # TODO: ....
    pass

class Plugin(PromptPlugin):
    """ Adds the path for the currently activated venv to the main prompt """
    def install(self):
        def adjust_prompt():
            """ there's probably a better way to do this, but
                ipython is not fully initialized when this
                plugin is installed.
            """
            prompt.add(showVenv)
        do_it_later(adjust_prompt, delay=2)
