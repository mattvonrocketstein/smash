""" smashlib.prompts.interface
    NB: prompt-related obviously, but this is not a prompt
"""

from smashlib.data import EDITOR_CONFIG_PATH
from smashlib.handle import AbstractInterface


class PromptInterface(AbstractInterface):

    user_ns_var = 'prompt'

    @property
    def edit(self):
        self.smash.shell.run_cell('ed {0}'.format(EDITOR_CONFIG_PATH))

    def __qmark__(self):
        """ user-friendly information when the input is "prompts?" """
        out = ['Smash Prompts: ({0} total)'.format(len(self._prompts))]
        for nick in self._prompts:
            out += ['   : {0}'.format(nick)]
        return '\n'.join(out)

    @property
    def _prompts(self):
        return [1, 2, 3]  # self.smash._installed_prompts

    # def __getitem__(self, prompt_name):
    #    return self._prompts[prompt_name]

    def update(self):
        return
        tmp = self._prompts

        def fxn(name):
            return self.smash._installed_prompts[name]
        for name in tmp:
            tmp2 = lambda himself: fxn(name)
            tmp3 = self.smash._installed_prompts[name].__qmark__()
            tmp2.__doc__ = tmp3
            prop = property(tmp2)
            setattr(self.__class__, name, prop)
        whitelist = ['edit', 'smash', 'update']
        for x in dir(self):
            if not x.startswith('_') and \
                    x not in tmp and \
                    x not in whitelist:
                raise ValueError("interface is not clean")
