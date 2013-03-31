""" host_prompt
"""
import platform
from smashlib.prompt import prompt, PromptComponent
from smashlib.smash_plugin import SmashPlugin

class Plugin(SmashPlugin):
    """ """
    def install(self):
        report('installing host-prompt')
        prompt.add(
            PromptComponent(name='host',priority=1,
                            template=platform.node()))
