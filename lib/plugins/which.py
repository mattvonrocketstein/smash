"""
"""
from smashlib.plugins import Plugins, SmashPlugin

def which(input):
    error = os.system('which '+input)
    if error:
        return pywhich(..)

class Plugin(SmashPlugin):
    """
    """
    def install(self):
        self.contribute('which', which)
