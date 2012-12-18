"""
"""
import notify2
import time
import processing, threading
from smashlib.smash_plugin import SmashPlugin
DEFAULT_TIMEOUT = 2
class Plugin(SmashPlugin):
    def install(self):
        def cb(*args,**kargs):
            print 'this is the callback!'
        self.contribute(note=lambda: build_note('title',message='body', callback=cb))
        self.icontribute(notification=notify2.Notification)
        self.contribute(processing=processing)


class MyNotification(notify2.Notification):
    def show(self):
        out = super(MyNotification, self).show()
        print 'notification id:',self.id
        return out

def build_note(*args, **kargs):
    if 'timeout' not in kargs:
        kargs['timeout'] = DEFAULT_TIMEOUT
    target1 = lambda: _build_note(*args, **kargs)
    target2 = lambda: [time.sleep(kargs['timeout']+3),
                       report('killing proc'),
                       proc.terminate()]
    proc = processing.Process(target=target1)
    thr= threading.Thread(target=target2)
    thr.start(), proc.start()
    return proc,thr

def _build_note(title, callback=None, **kargs):
    """ this function is blocking,
        and cannot be run from a thread!

        if the notification is clicked, with or without a
        callback, it might only block for a short period time.

        if the user ignores the callback, and the timeout is reached,
        the message disappears from the screen (and remains in the queue)
        but the mainloop still never exits.  adding a callback for
        the 'close' signal still didn't fix this.
    """
    import gtk
    notify2.init('smash-shell', 'glib')
    timeout=kargs.pop('timeout')
    n = MyNotification(title,
                       icon="notification-message-im",
                       **kargs)
    if callback is not None:
        def wrapped_callback(*args, **kargs):
            out = callback(*args,**kargs)
            print 'closing'
            n.close()
            gtk.main_quit()
            return out
        n.add_action('action','label',wrapped_callback,user_data=None)
    n.timeout = timeout#*1000
    n.show()
    gtk.main()
