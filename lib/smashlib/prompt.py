# -*- coding: utf-8
""" smash.prompt """

import os
from collections import namedtuple
from smashlib.util import get_term_colors, this_venv

tc = get_term_colors()
DEFAULT_SORT_ORDER = 2
__IPYTHON__._this_venv = this_venv
__IPYTHON__._this_wd = lambda: os.getcwd()

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
            try:
                color = getattr(tc, self.color)
            except AttributeError:
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
            raise Exception,'expected prompt component, got: ' + str(v)
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

showVenv = PromptComponent(
    name='venv_path',
    priority=DEFAULT_SORT_ORDER, color='yellow',
    template='''${getattr(__IPYTHON__, '_this_venv', lambda: "")()}''')

showWorkingDir = PromptComponent(name='working_dir',
                                 priority=100,
                                 #template=u'\Y3',
                                 template='''${getattr(__IPYTHON__, '_this_wd', lambda: "")()}''',
                                 color='green')

showBase =PromptComponent(name='prompt_base',
                          priority=10000, template=u'\n┕> ', color='green')

prompt  = Prompt()
#prompt.__setitem__(showWorkingDir.name, showWorkingDir, update=False)
prompt[showWorkingDir.name]= showWorkingDir
prompt[showBase.name]= showBase
