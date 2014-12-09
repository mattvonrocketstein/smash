""" smashlib.config.schemas
"""

from voluptuous import Schema as _Schema
from voluptuous import Required, Invalid
from IPython.terminal.interactiveshell import get_default_editor

from smashlib.config import templates

class Schema(_Schema):
    def __init__(self, validator, default=None):
        self.default = default
        super(Schema, self).__init__(validator)

def SimpleStringDict(x):
    for k, v in x.items():
        if not isinstance(k, basestring):
            raise Invalid("{0} is not a string".format(k))
        if not isinstance(v, basestring):
            raise Invalid("{0} is not a string".format(k))

def AliasListDict(x):
    for k, v in x.items():
        if not isinstance(k, basestring):
            raise Invalid("{0} is not a string".format(k))
        if not isinstance(v, list):
            raise Invalid("{0} is not a list".format(k))
        for i in v:
            if not isinstance(i, list) or not len(i)==2:
                err = ("aliases[{0}][{1}]='{2}' should be an array "
                       "of length 2 (first element is alias, second "
                       "element is command)").format(k,v.index(i),i)
                raise Invalid(err)


aliases = Schema(AliasListDict, templates.aliases)
macros = Schema(AliasListDict, templates.macros)

search_dirs = Schema(list, [])
venvs = Schema(SimpleStringDict, {})
projects = Schema(SimpleStringDict, {})

editor = Schema(
    {Required("console") : unicode,
     Required("window_env") : unicode,},
    default=dict(window_env=get_default_editor(),
                 console=get_default_editor())
                )
