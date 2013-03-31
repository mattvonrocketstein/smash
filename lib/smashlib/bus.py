from cyrusbus import Bus

def fac(m):
    from smashlib.util import report_if_verbose
    return lambda bus, *args, **kargs: getattr(report_if_verbose, m)(str(kargs) )


bus = Bus()
bus.subscribe('post_invoke',   fac('post_invoke'))
bus.subscribe('pre_invoke',    fac('pre_invoke'))
bus.subscribe('pre_activate',  fac('pre_activate'))
bus.subscribe('post_activate', fac('post_activate'))
bus.subscribe('pre_deactivate',  fac('pre_deactivate'))
bus.subscribe('post_deactivate', fac('post_deactivate'))
