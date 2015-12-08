""" smashlib.prompts.interface
    NB: prompt-related obviously, but this is not a prompt
"""

from smashlib.data import PROMPT_CONFIG_PATH
from smashlib.handle import AbstractInterface
from smashlib import get_smash

class PromptInterface(AbstractInterface):

    _user_ns_var = 'prompt'

    @property
    def edit(self):
        get_smash().shell.run_cell('ed {0}'.format(PROMPT_CONFIG_PATH))

    def __qmark__(self):
        """ user-friendly information when the input is "prompts?" """
        out = ['Smash Prompts: ({0} total)'.format(len(self._prompts))]
        for i, component in enumerate(self._prompts):
            component=component.copy()
            component.pop('space_margins')
            out += [' {0}: {1}'.format(i, component)]
        return '\n'.join(out)

    @property
    def _prompts(self):
        return get_smash().prompt_manager.prompt_components

    def update(self):
        return
        tmp = self._prompts

        def fxn(name):
            return self.smash._installed_prompts[name]
        for name in tmp:
            tmp2 = lambda himself: fxn(name)
            tmp3 = get_smash()._installed_prompts[name].__qmark__()
            tmp2.__doc__ = tmp3
            prop = property(tmp2)
            setattr(self.__class__, name, prop)
        whitelist = ['edit', 'smash', 'update']
        for x in dir(self):
            if not x.startswith('_') and \
                    x not in tmp and \
                    x not in whitelist:
                raise ValueError("interface is not clean")
