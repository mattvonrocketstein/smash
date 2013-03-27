""" smash.prompt """
from smashlib.data import PROMPT_DEFAULT as DEFAULT

class Prompt(dict):

    def __setitem__(self, k, v, update=True):
        if k in self:
            raise Exception,'prompt component is already present: ' + str(k)
        super(Prompt, self).__setitem__(k, v)
        if update:
            self.update_prompt()

    def update_prompt(self):
        parts = self.values()
        parts.sort()
        parts = [part[1] for part in parts]
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
prompt.__setitem__('working_dir', [100, DEFAULT], update=False)
prompt.template = DEFAULT
