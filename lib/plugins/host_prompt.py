""" host_prompt
"""
import platform
from smashlib.prompt import prompt, PromptComponent
from smashlib.smash_plugin import SmashPlugin

class Plugin(SmashPlugin):
    """ """
    def install(self):
        report.host_prompt('installing')
        prompt['host'] = PromptComponent(
            name='host', priority=1, color='blue',
            template=os.environ['USER']+'@'+platform.node())
