""" smashlib.smash_plugin
"""
import os
from collections import defaultdict

from smashlib.util import report, list2table
from smashlib.reflect import namedAny

def track_changes(fxn):
    def newf(self, *args, **kargs):
        self.changes[fxn.__name__].append([args, kargs])
        return fxn(self, *args, **kargs)
    return newf

class SmashPlugin(object):
    """ to make a new plugin for SmaSh, extend this class """

    # TODO: dont use this, use spock constraints
    installation_priority = 10
    requires = []
    requires_plugins = []

    # track any changes made by this plugin
    # so we can (theoretically) invert them later
    inversions = dict(alias = 'unalias',
                      contribute = NotImplemented,
                      # 'delete_magic'
                      contribute_magic = NotImplemented,
                      )

    def __qmark__(self):
        my_report = getattr(report, self.name)
        _help = defaultdict(lambda:'')
        _help.update({
            'Macro': '\n  Type "{cmd}.value" to see macro definition.\n',
            'python function': '\n  Type "{cmd}??" to see fxn definition.\n',
            # next is wrong because ipy says "[source file open failed]"
            'python class': '\n  Type "{cmd}??" to see kls definition.\n',
            })

        def get_type_info(x):
            try:
                x.__name__
            except AttributeError:
                tmp = x.__class__.__name__
                tmp = tmp if tmp=='Macro' else 'python class'
                return tmp
            else:
                tmp = type(x).__name__
                if tmp=='function':
                    tmp='python function'
                return tmp

        if not self.changes:
            my_report("this is a plugin, it's not installed yet.")
            # nitpick, but actually it might just have no side-effects..
        else:
            my_report("This plugin is installed, and has modified the interpretter.")
            my_report("What follows is a summary of this plugin contributions:")
            for contribution in self.changes['contribute']:
                cargs, ckargs = contribution
                cname, cvalue = cargs
                ty = get_type_info(cvalue)
                report(''.join([
                    '  {red}',cname,
                    '{normal} is a {red}',
                    ty+'{normal}.'+_help[ty].format(cmd=cname)]))


    def __init__(self):
        self.changes = defaultdict(list)

    @track_changes
    def set_env(self, name, val):
        os.environ[name] = val

    @track_changes
    def add_hook(self, *args,**kargs):
        from smashlib.util import add_hook
        return add_hook(*args, **kargs)

    @track_changes
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

    @track_changes
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
        """ FIXME: not used yet """
        self.verify_requirements()

    @track_changes
    def contribute_magic(self, name, func):
        if name.startswith('magic_'):
            magic_name = name
        else:
            magic_name = 'magic_{0}'.format(name)
        setattr(__IPYTHON__, magic_name, func)
        return func
