""" simple completion for python setup.py

    want to trigger completion for stuff like this:
      python setup.py<tab>
      ./python setup.py<tab>
      python ./setup.py<tab>
      python2.7 ./setup.py<tab>
      .. etc

    additionally, because setup.py might add new scripts to
    bin directories, always trigger a rehash after setup.py
    is invoked
"""

from smashlib.util import set_complete, add_hook
from smashlib.smash_plugin import SmashPlugin
from IPython.ipapi import TryNext

setup_re = 'python.*setup.py'

# TODO: something very much like this
#       after running 'make install' or apt
def setup_py_hook(*args, **kargs):
    last_line  =__IPYTHON__.user_ns['In'][-1]
    sys_call_start = '_ip.system('
    if last_line.startswith(sys_call_start):
        # might be " or '.  TODO: regex
        quote_char = last_line[len(sys_call_start):][0]
        # get the thing inbetween the quotes
        sys_cmd = last_line.split(quote_char)[1]
        sys_cmd = sys_cmd.strip()
        # FIXME: probably just use setup_re
        if 'python' in sys_cmd and 'setup.py' in sys_cmd:
            report.setup_py("detected that you ran setup.py.. "
                            "rehashing env")
            __IPYTHON__.magic_rehashx()
    raise TryNext()

class Plugin(SmashPlugin):
    def install(self):
        completer = lambda *args,**kargs: ['build', 'develop','install']
        set_complete(completer, setup_re)
        # the specific hook choice and priority here is pretty
        # arbitrary.. whatever it seems to work.
        self.add_hook('generate_prompt', setup_py_hook, 0)
