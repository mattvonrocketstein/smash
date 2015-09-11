""" smashlib.plugins.prompt
"""

#from IPython.utils.traitlets import Bool, Unicode

from smashlib.plugins import Plugin
from smashlib.config import SmashConfig
from smashlib.prompt.component import PromptComponent
from smashlib._logging import smash_log

DEFAULT_IN_TEMPLATE = u'In [\\#]: '

DEFAULT_PROMPT = [
    PromptComponent(
        type='env',
        value='$USER'),
    PromptComponent(
        type='literal', value=':'),
    PromptComponent(
        type='python',
        value="smashlib.prompt.working_dir"),
    PromptComponent(
        type='literal', value=' ',),
    PromptComponent(
        type='python',
        value='smashlib.prompt.git_branch',
        color='blue',),
    PromptComponent(
        type='python',
        value='smashlib.prompt.user_symbol',
        color='red',),
    PromptComponent(
        type='python',
        value='smashlib.prompt.venv',
        color='yellow',),
]


class SmashPrompt(Plugin):

    """ this extension requires ipy_cd_hook """

    def uninstall(self):
        super(SmashPrompt, self).uninstall()
        self.shell.prompt_manager.in_template = DEFAULT_IN_TEMPLATE

    # def init_magics(self):
    #    self.contribute_magic(prompt_tag)

    def _load_prompt_config(self):
        c = SmashConfig()
        components = c.load_from_etc('prompt.json')
        if not components:
            components = DEFAULT_PROMPT
        out = []
        for component in components:
            out.append(PromptComponent(**component))
        components = out
        self.prompt_components = components

    def init(self):
        smash_log.info("initializing")
        self._load_prompt_config()
        self.update_prompt()
        self.contribute_hook('pre_prompt_hook', self.update_prompt)

    def update_prompt(self, himself=None):
        tmp = self.get_prompt()
        self.shell.prompt_manager.update_prompt('in', tmp)

    def get_prompt(self):
        prompt = '\n'
        for component in self.prompt_components:
            smash_log.debug("calling prompt component: " + str(component))
            assert callable(component), str(
                "bad prompt component: " + str(component))
            prompt += component()
        prompt = prompt.replace('  ', ' ')
        return prompt


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    sp = SmashPrompt(ip)
    #ip._smash.sp = sp
    return sp
