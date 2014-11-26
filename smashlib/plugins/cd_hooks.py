""" smashlib.ipy_cd_hooks

"""
from IPython.utils.traitlets import EventfulList

from smashlib.v2 import Reporter
from smashlib.util.reflect import from_dotpath, ObjectNotFound
from smashlib.channels import C_CD_EVENT
from smashlib.patches import PatchCDMagic, PatchPushdMagic


class ChangeDirHooks(Reporter):

    last_dir = None
    change_dir_hooks = EventfulList(default_value=[], config=True)

    def init(self):
        # FIXME: reregister it properly instead of patching it?
        if not getattr(self, '_already_patched', False):
            mycd = PatchCDMagic(self)
            mypushd = PatchPushdMagic(self, mycd)
            mycd.install()
            mypushd.install()
            self._already_patched = True
            self.report("finished patching cd magic")
        else:
            self.report("cd magic is already patched")

    def _event_set_change_dir_hooks(self, slice_or_index, val):
        try:
            obj = from_dotpath(val)
        except ObjectNotFound as e:
            err = 'ChangeDirHooks.change_dir_hooks: '
            raise ObjectNotFound(err+e.message)
        self.report("retrieved from dotpath: ", obj)
        self.report("object will be subscribed to <{0}>".format(C_CD_EVENT))
        self.smash.bus.subscribe(C_CD_EVENT, obj)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    return ChangeDirHooks(ip)

def unload_ipython_extension(ip):
    original = ChangeDirHooks.original_cd_magic
    assert original is not None
    ip.shell.magics_manager.magics['line']['cd'] = original