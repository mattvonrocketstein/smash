""" smashlib.patches.edit
"""
#from smashlib.patches.base import PatchMagic
from IPython.core.magics.code import CodeMagics


class PatchEdit(object):
    """ patches the builtin ipython cd magic so that a post-dir-change
        event can be sent to anyone who wants to subscribe, and so that
        the "cd" command is quiet by default.
    """
    original = staticmethod(CodeMagics._find_edit_target)
    def __init__(self, *args, **kargs):
        pass

    def install(self):
        CodeMagics._find_edit_target = my_find_edit_target

def my_find_edit_target(himself,shell,args,opts,last_call):
    """Utility method used by magic_edit to find what to edit."""
    if args.endswith(':'):
        args=args[:-1]
    result = PatchEdit.original(shell,args,opts,last_call)
    if result==(None,None,None):
        filename, lineno, use_temp=(args, None, False)
        return filename, lineno, use_temp
    return result
