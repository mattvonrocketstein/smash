""" ipy_liquidprompt

    Uses the liqiuidprompt project to render the ipyton prompt.
    NOTE: liquidprompt itself requires bash or zsh
"""
import os
import subprocess
from subprocess import PIPE

from IPython.utils.traitlets import Bool, Unicode

from smashlib.v2 import Reporter
from smashlib.util.events import receives_event
from smashlib.channels import C_UPDATE_PROMPT_REQUEST

lp_f = os.path.join(os.path.dirname(__file__), 'liquidprompt')

def prompt_tag(parameter_s=''):
    """ set prompt tag prefix """
    if parameter_s:
        parameter_s=' '+parameter_s
    os.environ['LP_PS1_PREFIX'] = parameter_s

class LiquidPrompt(Reporter):
    """ this extension requires ipy_cd_hook """

    float    = Bool(True, config=True, help="add more space between prompts")
    prompt_append = Unicode("", config=True, help="add more space between prompts")

    @receives_event(C_UPDATE_PROMPT_REQUEST)
    def update_prompt_on_request(self, request_from):
        "NOTE: really need to update prompt every time anything has run.."
        #self.update_prompt()
        pass

    def init_magics(self):
        self.contribute_magic(prompt_tag)

    def init(self):
        self.update_prompt()
        self.shell.set_hook(
            'pre_prompt_hook',
            lambda himself: self.update_prompt())

    def update_prompt(self):
        tmp = self.get_prompt().strip() + self.prompt_append
        if self.float==True:
            tmp = '\n' + tmp
        self.shell.prompt_manager.in_template = tmp

    def get_prompt(self):
        cmd = unicode('bash '+lp_f).format(os.getcwd())
        env = os.environ.copy()
        env.update(LP_HOSTNAME_ALWAYS="true",PS1="",)
        dict(
            TERM='xterm',
            LP_HOST='fakehost',
            PWD = os.getcwd(),
            USER=os.environ['USER'],
            BASH_VERSION='4.3.11(1)-release',
            VIRTUAL_ENV=os.environ.get('VIRTUAL_ENV',''),
            )
        tmp = subprocess.Popen(cmd, shell=True,
                               env=env, stdout=PIPE)
        o,e = tmp.communicate()
        return o.decode('utf-8')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    lp = LiquidPrompt(ip)
    ip._smash.lp = lp
    return lp

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'