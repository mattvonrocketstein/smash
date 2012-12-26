""" smashlib.smash_plugin
"""
from IPython import ipapi

from smashlib.util import report
from smashlib.reflect import namedAny

ip = ipapi.get()

class SmashPlugin(object):
    """ to make a new plugin for SmaSh, extend this class """
    installation_priority = 10
    requires = []
    requires_plugins = []

    def unalias(self, name):
        return __IPYTHON__.magic_unalias(name)

    def __repr__(self):
        return '<SmashPlugin@"{0}">'.format(self.name)

    def verify_requirements(self):
        report('pretending to verify requirements: {0}'.format(self.requires))
        print 'installing',self
        from smashlib.reflect import namedAny
        raise Exception, 'niy'
        for name in self.requires:
            obj = namedAny(name)

    def install_into_smash(self):
        """ install this plugin into the smash shell """
        self.verify_requirements()
        self.install()

    def float_names(self, names):
        """import names and add them to the global interpretter namespace """
        return [ self.float_name(name) for name in names ]
    def ifloat_names(self, names):
        """ import names and add them (and their lowercase equivalent)
            to the global interpretter namespace """
        return [ self.ifloat_name(name) for name in names ]
    def ifloat_name(self, name):
        """ import name and add it (and its lowercase equivalent)
            to the global interpretter namespace """
        return self.icontribute(name.split('.')[-1], namedAny(name))
    def float_name(self, name):
        """ import name and add them to the global interpretter namespace """
        return self.contribute(name.split('.')[-1], namedAny(name))
    def icontribute(self,*args, **kargs):
        """  contribute name/val (and lowercase equivalent
             to the global interpretter namespace
        """
        kargs.update(case_sensitive=False)
        return self.contribute(*args, **kargs)

    def contribute(self, *args, **kargs): #case_sensitive=True):
        """ contribute name/val to IPython shells' namespace """
        case_sensitive = kargs.pop('case_sensitive',False)
        name, val = None, None
        if len(args)==2:
            name, val= args
        else:
            assert len(kargs)==1, 'not implemented yet, maybe never..'
            name,val = kargs.items()[0]

        if name in __IPYTHON__.user_ns:
            msg = ('"{0}" variable is taken in user namespace.  '
                   'refusing to proceed').format(name)
            report.plugin(msg)
        else:
            ctx = {name:val}
            if not case_sensitive: ctx.update({name.lower():val})
            __IPYTHON__.user_ns.update(**ctx)
        return val

    def pre_install(self):
        """ TODO: not used yet """
        self.verify_requirements()

    def contribute_magic(self, name, func):
        if name.startswith('magic_'):
            magic_name = name
        else:
            magic_name = 'magic_{0}'.format(name)
        setattr(__IPYTHON__, magic_name, func)
        return func
