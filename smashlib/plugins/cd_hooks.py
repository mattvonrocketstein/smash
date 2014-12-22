""" smashlib.plugins.cd_hooks

"""
from IPython.utils.traitlets import EventfulList

from smashlib.plugins import Plugin
from smashlib.util.reflect import from_dotpath, ObjectNotFound
from smashlib.channels import C_CHANGE_DIR
from smashlib.patches import PatchCDMagic, PatchPushdMagic


class ChangeDirHooks(Plugin):

    last_dir = None
    change_dir_hooks = EventfulList(default_value=[], config=True)

    def init(self):
        # FIXME: reregister it properly instead of patching it?
        # FIXME: this check is probably no needed since patching cannot happen twice
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
        self.report("object will be subscribed to <{0}>".format(C_CHANGE_DIR))
        self.smash.bus.subscribe(C_CHANGE_DIR, obj)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return ChangeDirHooks(get_ipython()).install()

def unload_ipython_extension(ip):
    original = ChangeDirHooks.original_cd_magic
    assert original is not None
    ip.shell.magics_manager.magics['line']['cd'] = original
