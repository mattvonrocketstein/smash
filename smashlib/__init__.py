""" smashlib
"""
__version__ = 0.1

def start_ipython(argv=None, **kwargs):
    from smashlib.overrides import launch_new_instance
    return launch_new_instance(argv=argv, **kwargs)

def embed(argv=tuple(), **kargs):
    import os
    if os.environ.get('SMASH', None):
        print "..detected nesting.. this may cause problems"

    from goulash._inspect import get_caller
    context = kargs.pop('user_ns', {})
    caller_context = get_caller(2)
    context.update(caller_context['globals'])
    context.update(caller_context['locals'])
    start_ipython(argv=argv, user_ns=context, **kargs)

def get_smash():
    try:
        ip = get_ipython()
    except NameError:
        return None
    try:
        return ip._smash
    except AttributeError:
        raise Exception("load smash first")
