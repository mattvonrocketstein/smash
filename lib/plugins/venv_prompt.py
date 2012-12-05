""" venv_prompt
"""
import os
from threading import Thread
from smashlib.util import get_prompt_t, set_prompt_t
from smashlib.plugins import Plugins, SmashPlugin

def this_venv():
    result = os.environ.get('VIRTUAL_ENV','')
    result = result.replace(os.environ['HOME'],'~')
    result = os.path.sep.join(result.split(os.path.sep)[-2:])
    return '({0})'.format(result)

class Plugin(SmashPlugin):
    """    """
    def install(self):
        def delayed():
            """ there's probably a better way to do this, but
                ipython is not fully initialized when this
                plugin is installed.
            """
            import time; time.sleep(2)
            __IPYTHON__._this_venv = this_venv
            t = '''${getattr(__IPYTHON__, '_this_venv', lambda: "")()}''' + get_prompt_t()
            set_prompt_t(t)
        Thread(target=delayed).start()
