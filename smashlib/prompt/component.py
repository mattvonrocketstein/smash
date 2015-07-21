""" smashlib.prompt.component
"""

import os
import addict
from goulash._fabric import qlocal
from smashlib.util.reflect import from_dotpath


class PromptError(ValueError):
    pass


class PromptComponent(addict.Dict):

    TYPES = 'python shell env literal'.split()

    def __call__(self):
        if self.type == 'python':
            fxn = from_dotpath(self.value)
            if not callable(fxn):
                err = ("prompt component {0} references "
                       "something that's not callable!")
                err = err.format(dict(self))
                raise PromptError(err)
            result = fxn()
        elif self.type == 'literal':
            result = self.value
        elif self.type == 'shell':
            result = qlocal(self.value, capture=True).strip()
        elif self.type == 'env':
            if self.value.startswith('$'):
                value = self.value[1:]
            else:
                value = self.value
            result = os.environ.get(value, '')
        else:
            err = 'invalid prompt component: {0}'
            err = err.format(self)
            raise Exception(err)
        # post-processing
        if result and self.space_margins:
            if self.space_margins == True or \
                    self.space_margins.lower() == 'true':
                result = ' {0} '.format(result)
        if self.color:
            # have to use IPython's formatting rules so that IPython
            # can correctly calculate terminal width w/ invisible chars
            return '{color.' + self.color.title() + '}' + result + '{color.Normal}'
        else:
            return result
