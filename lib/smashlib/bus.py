""" smashlib.bus
"""

from cyrusbus import Bus

def _verbose(m):
    from smashlib.util import report_if_verbose
    return lambda bus, *args, **kargs: getattr(report_if_verbose, m)(str(kargs) )

def _standard(m):
    from smashlib.util import report
    return lambda bus, *args, **kargs: getattr(report, m)(str(kargs) )

def _warning():
    from smashlib.util import report
    return lambda bus, *args, **kargs: getattr(report, 'WARNING')(args[0])

bus = Bus()
bus.subscribe('post_invoke',     _verbose('post_invoke'))
bus.subscribe('pre_invoke',      _verbose('pre_invoke'))
bus.subscribe('pre_activate',    _verbose('pre_activate'))
bus.subscribe('post_activate',   _verbose('post_activate'))
bus.subscribe('pre_deactivate',  _verbose('pre_deactivate'))
bus.subscribe('post_deactivate', _verbose('post_deactivate'))
bus.subscribe('warning',         _warning())
bus.warning = lambda msg: bus.publish('warning', msg)
