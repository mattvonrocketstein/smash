""" open urls for various places around medley
"""
from webbrowser import open_new_tab

def ont(url):
    print url
    open_new_tab(url)

class Show(object):
    """ opens pages in your webbrowser for common tasks.
    """
    class Intranet(object):
        base_url = 'http://intranet.cmgdigital.com/display/collaboration/'
        def fe_signup(self):
            ont(self.base_url + 'Using+Feature+Environments')
        def psas(self):
            ont(self.base_url + 'PSAs')
            intranet=Intranet()
    intranet = Intranet()

    class Hudson(object):
        base_url = 'https://hudson.cmgdigital.com/'

        def login(self):
            ont(self.base_url + 'login?from=%2F')
    hudson = Hudson()
    @staticmethod
    def hudson_job(vm_num):
        url = Hudson.base_url + 'job/FE{N}-Test/'
        url = url.format(N=vm_num)
        ont(url)

    class Munin(object):
        base_url = 'http://munin.ddtc.cmgdigital.com/cmgdigital.com/'
        def celery_for(self, vm_num):
            url = self.base_url + "vm{N}.cmgdigital.com/index.html#rabbitmq"
            url = url.format(N=vm_num)
            ont(url)
        class Celery(object): pass
        celery = Celery()
    munin = Munin()
    def tmp2(i): return property(lambda self: Show.munin.celery_for(i))
    for i in '123456789':
        setattr(Munin.Celery, '_'+i, tmp2(i))

    @staticmethod
    def review(num):
        ont('http://reviews.ddtc.cmgdigital.com/r/'+str(num))

# hack to install several properties on the fly
#def tmp1(i): return property(lambda self: Show.hudson_job(i))
#def tmp2(i): return property(lambda self: Show.celery(i))
#for i in '123456789':
#    setattr(Show, 'hfe_'+i, tmp1(i))
#    setattr(Show, 'celery_vm'+i, tmp2(i))
