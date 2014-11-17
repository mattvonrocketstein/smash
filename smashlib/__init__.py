""" smashlib
"""
__version__ = 0.1

def start_ipython(argv=None, **kwargs):
    #from smashlib.python import ModPath
    #modpath = ModPath.install()
    from smashlib.overrides import launch_new_instance
    return launch_new_instance(argv=argv, **kwargs)

def embed(argv=tuple(), **kargs):
    from goulash._inspect import get_caller
    context = kargs.pop('user_ns', {})
    caller_context = get_caller(2)
    context.update(caller_context['globals'])
    context.update(caller_context['locals'])
    start_ipython(argv=argv, user_ns=context, **kargs)
