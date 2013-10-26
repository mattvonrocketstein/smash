""" simple completion for python setup.py

    want to trigger completion for stuff like this:
      python setup.py<tab>
      ./python setup.py<tab>
      python ./setup.py<tab>
      python2.7 ./setup.py<tab>
      .. etc

    additionally, because setup.py might add new scripts to
    bin directories, always trigger alias rehash after setup.py
    is invoked
"""

from smashlib.util import set_complete, add_hook, last_command_hook
from smashlib.smash_plugin import SmashPlugin

setup_re = 'python.*setup.py'

# TODO: something very much like this
#       after running 'make install' or apt
@last_command_hook
def setup_py_hook(sys_cmd):
    # FIXME: probably just use setup_re
    if 'python' in sys_cmd and 'setup.py' in sys_cmd:
        report.setup_py("detected that you ran setup.py.. "
                        "rehashing env")
        __IPYTHON__.magic_rehashx()

class Plugin(SmashPlugin):
    def install(self):
        completer = lambda *args, **kargs: ['build', 'develop','install']
        set_complete(completer, setup_re)
        # the specific hook choice and priority here is
        # pretty arbitrary, but, it seems to work.
        self.add_hook('generate_prompt', setup_py_hook, 0)
