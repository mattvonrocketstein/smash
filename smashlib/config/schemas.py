""" smashlib.config.schemas
"""

from voluptuous import Schema as _Schema
from voluptuous import Required, Invalid
from IPython.terminal.interactiveshell import get_default_editor

from smashlib.util.reflect import from_dotpath
from smashlib.config import templates


class Schema(_Schema):

    def __init__(self, validator, default=None):
        self.default = default
        super(Schema, self).__init__(validator)

def ImportableStringList(x):
    for s in x:
        assert isinstance(s, basestring)
        try:
            from_dotpath(s)
        except Exception,e:
            raise Invalid(str(e))

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
            if not isinstance(i, list) or not len(i) == 2:
                err = ("aliases[{0}][{1}]='{2}' should be an array "
                       "of length 2 (first element is alias, second "
                       "element is command)").format(k, v.index(i), i)
                raise Invalid(err)

def EnvListDict(x):
    """TODO: dryer with AliasListDict """
    for k, v in x.items():
        if not isinstance(k, basestring):
            raise Invalid("{0} is not a string".format(k))
        if not isinstance(v, list):
            raise Invalid("{0} is not a list".format(k))
        for i in v:
            if not isinstance(i, list) or not len(i) == 2:
                err = ("env[{0}][{1}]='{2}' should be an array "
                       "of length 2 (first element is alias, second "
                       "element is command)").format(k, v.index(i), i)
                raise Invalid(err)


def PromptDict(lst):
    doc_url = 'http://placeholder'
    _types = 'python env shell literal'.split()
    err = ('The prompt.json entry at index {0} ("{1}") should be '
           'a dictionary where at least "type" and "value" are defined.  '
           'The value for "type" is one of {3}.  See the documentation at {4}')
    for x in lst:
        if 'type' not in x or 'value' not in x:
            raise Invalid(err.format(lst.index(x), x, _types, doc_url))
        if x['type'] not in _types:
            raise Invalid(err.format(lst.index(x), x, _types, doc_url))

aliases = Schema(AliasListDict, templates.aliases)
env = Schema(EnvListDict, templates.env)
macros = Schema(AliasListDict, templates.macros)

prompt = Schema(PromptDict, {})
search_dirs = Schema(list, [])

projects = Schema(SimpleStringDict, {})
venvs = Schema(SimpleStringDict, templates.venvs)
plugins = Schema(ImportableStringList, templates.plugins)
editor = Schema(
    { Required("console"): unicode,
      Required("window_env"): unicode, },
    default=dict(window_env=get_default_editor(),
                 console=get_default_editor())
)
