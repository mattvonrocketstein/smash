""" currency conversion:

      provides an input preprocess that allows for currency conversions.
      query must match a regex that recognizes stuff like this: '10 lkr to usd'

      http://segfault.in/2010/03/command-line-currency-converter-for-linux/
"""
#from IPython.hooks import CommandChainDispatcher
#__IPYTHON__.hooks['input_prefilter'] = CommandChainDispatcher(...)
from smashlib.smash_plugin import SmashPlugin
class Plugin(SmashPlugin):
    def install(self):
        'not implemented yet'
