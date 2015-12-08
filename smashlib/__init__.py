""" smashlib
"""
__version__ = 0.1
from goulash._inspect import get_caller
from smashlib.import_hooks import hijack_ipython_module


def start_ipython(argv=None, **kwargs):
    from smashlib.overrides import launch_new_instance
    return launch_new_instance(argv=argv, **kwargs)


def embed(argv=tuple(), **kargs):
    hijack_ipython_module()
    # if os.environ.get('SMASH', None):
    #    print "..detected nesting.. this may cause problems"
    context = kargs.pop('user_ns', {})
    caller_context = get_caller(2)
    if context is not None:
        context.update(caller_context['globals'])
        context.update(caller_context['locals'])
    if '--no-confirm-exit' not in argv:
        argv = ['--no-confirm-exit'] + list(argv)
    try:
        start_ipython(argv=argv, user_ns=context, **kargs)
    except KeyboardInterrupt:
        pass


def get_smash():
    try:
        ip = get_ipython()
    except NameError:
        return None
    try:
        return ip._smash
    except AttributeError:
        raise Exception("load smash first")
