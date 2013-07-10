""" smash.prompt """

from collections import namedtuple
from smashlib.data import PROMPT_DEFAULT as DEFAULT
from smashlib.util import get_term_colors
tc = get_term_colors()

class PromptComponent(object):
    """
    """
    def __init__(self, name=None, template=None, color=None,
                 priority=1, lazy=False, contributor=None):
        REQUIRED = 'name template'.split()
        OPTIONAL = 'priority lazy contributor color'.split()
        for x in REQUIRED:
            assert eval(x), x + ' is required'
        for x in OPTIONAL+REQUIRED:
            setattr(self, x, eval(x))

    def render(self):
        result = self.template
        if self.color:
            color = getattr(tc, self.color.title())
            result = ''.join([color, result, tc.Normal])
        return result

class Prompt(dict):
    """
    """
    def __setitem__(self, k, v, update=True):
        if k in self:
            raise Exception,'prompt component is already present: ' + str(k)
        if not isinstance(v, PromptComponent):
            raise Exception,'expected prompt component, got: '+str(v)
        super(Prompt, self).__setitem__(k, v)
        if update:
            self.update_prompt()

    def add(self, pc):
        self.__setitem__(pc.name, pc)

    def update_prompt(self):
        parts = self.values()
        parts.sort(lambda x,y: cmp(x.priority,y.priority))
        parts = [ pc.render() for pc in parts]
        self.template = ' '.join(parts)

    def _get_template(self):
        """ get the current prompt template """
        opc = getattr(__IPYTHON__.shell, 'outputcache', None)
        if opc:
            return opc.prompt1.p_template
        else:
            return 'error-getting-output-prompt'
    def _set_template(self, t):
        """ set the current prompt template """
        opc = getattr(__IPYTHON__.shell, 'outputcache', None)
        if opc:
            opc.prompt1.p_template = t
    template = property(_get_template, _set_template)

prompt = Prompt()
working_dir = PromptComponent(name='working_dir', priority=100, template=DEFAULT)
prompt.__setitem__(working_dir.name, working_dir, update=False)
prompt.template = DEFAULT
