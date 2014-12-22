""" smashlib.plugins.post_input

    This plugin is responsible for doing the
    work whenever smash is invoked with "-c".
    Semantics are the same as "python -c" or
    "bash -c"

"""

from smashlib.plugins import Plugin
from smashlib.util.events import receives_event
from smashlib.channels import C_POST_RUN_INPUT

# a list of commands that could change the contents of $PATH;
# if this stuff happens then smash needs to recompute cache
REHASH_IF = [
    'setup.py develop',
    'pip install',
    'setup.py install',
    'apt-get install']

class PostInput(Plugin):
    verbose = True
    command = None

    @receives_event(C_POST_RUN_INPUT, quiet=True)
    def input_finished_hook(self, raw_finished_input):
        for x in REHASH_IF:
            if x in raw_finished_input:
                self.report("detected possible $PATH changes (rehashing)")
                self.smash.shell.magic('rehashx')

def load_ipython_extension(ip):
    ip = get_ipython()
    return PostInput(ip).install()


from smashlib import get_smash
from goulash.python import splitext,ops
def unload_ipython_extension(ip):
    plugin_name = splitext(ops(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
