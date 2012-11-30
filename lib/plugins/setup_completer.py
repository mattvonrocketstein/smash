""" simple completion for python setup.py

    want to trigger on:
      python setup.py<tab>
      python ./setup.py<tab>
      python2.7 ./setup.py<tab>
      .. etc
"""

from smashlib.util import set_complete
from smashlib.plugins import SmashPlugin

setup_re = 'python.*setup.py'

class Plugin(SmashPlugin):
    def install(self):
        completer = lambda *args,**kargs: ['build', 'develop','install']
        set_complete(completer, setup_re)
