""" smashlib.prompt.component
"""

import os
import addict
#from report import console
from IPython.utils import coloransi
from smashlib.util.reflect import from_dotpath
from goulash._fabric import qlocal

class PromptError(ValueError):
    pass

class PromptComponent(addict.Dict):

    TYPES = 'python shell env literal'.split()

    def __call__(self):
        if self.type == 'python':
            fxn = from_dotpath(self.value)
            if not callable(fxn):
                err = "prompt component {0} references something that's not callable!"
                err = err.format(dict(self))
                raise PromptError(err)
            result = fxn()
        elif self.type == 'literal':
            result = self.value
        elif self.type=='shell':
            result = qlocal(self.value, capture=True).strip()
        elif self.type=='env':
            result = os.environ.get(self.value,'')
        else:
            raise Exception('invalid prompt component type: {0}'.format(self.type))
        if self.color:
            #return getattr(coloransi.TermColors, self.color.title())+\
            #       result + coloransi.TermColors.Normal
            return '{color.'+self.color.title()+'}'+result+'{color.Normal}'
        else:
            return result
