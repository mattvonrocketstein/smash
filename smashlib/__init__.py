""" smashlib
"""
__version__ = 0.1

def start_ipython(argv=None, **kwargs):
    from smashlib.overrides import launch_new_instance
    return launch_new_instance(argv=argv, **kwargs)

def embed(argv):
    #from IPython import start_ipython
    start_ipython(argv=argv)
