# -*- coding: utf-8
""" smash.prompt """

import os
from collections import namedtuple
from smashlib.util import TERM_COLORS, this_venv, truncate_fpath
from smashlib.python import ops
DEFAULT_SORT_ORDER = 2

def this_wd():
    """ computes how the working directory will be displayed.
        directories under /home/$USER will be truncated to
        display tilda-style, and "%" is used as a shortcut for
        the root of any known project.

        TODO: "cd %/lib/foo/bar" should work like "~/lib/foo/bar"
    """
    from smashlib.util import this_project
    tmp = os.getcwd()
    proj = this_project()
    if proj is not None:
        if tmp.startswith(proj.dir):
            tmp = '%'+tmp[len(proj.dir):]
    return truncate_fpath(tmp)

# HACK
__IPYTHON__._this_venv = this_venv
__IPYTHON__._this_wd = this_wd

class PromptComponent(object):
    """ """

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
                color = getattr(TERM_COLORS, self.color)
            except AttributeError:
                color = getattr(TERM_COLORS, self.color.title())
            result = ''.join([color, result, TERM_COLORS.Normal])
        return result

# TODO: use ordered dict here
class Prompt(dict):
    """ main abstraction representing the prompt.
        this is where promptcomponents are tracked,
        ordered, added, and removed.
    """
    def __setitem__(self, k, v, update=True):
        if k in self:
            err = 'prompt component is already present: ' + str(k)
            raise Exception, err
        if not isinstance(v, PromptComponent):
            err = 'expected prompt component, got: ' + str(v)
            raise Exception, err
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

def dynamic_component_template(fxn_name):
    return '''${getattr(__IPYTHON__, \''''+fxn_name+'''\', lambda: "")()}'''

showVenv = dict(
    color='yellow',
    name='venv_path',
    priority=DEFAULT_SORT_ORDER,
    template=dynamic_component_template('_this_venv'),)
showBase = dict(
    color='green',
    priority=10000,
    template=u'\n\n┕> ',
    name='prompt_base',)
showWorkingDir = dict(
    priority=100,
    color='green',
    name='working_dir',
    template=dynamic_component_template('_this_wd'),)

showWorkingDir = PromptComponent(**showWorkingDir)
showBase       = PromptComponent(**showBase)
showVenv       = PromptComponent(**showVenv)

# declare the default prompt. most SmaSh users
# will want plugins that override or add to this
prompt  = Prompt()
prompt.add(showWorkingDir)
prompt.add(showBase)
