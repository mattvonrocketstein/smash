""" host_prompt
"""
import platform
from smashlib.prompt import prompt
from smashlib.smash_plugin import SmashPlugin

class Plugin(SmashPlugin):
    """ """
    def install(self):
        report('installing host-prompt')
        prompt['host'] = [1, platform.node()]
