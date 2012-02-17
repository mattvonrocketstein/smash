"""
"""

import os

import IPython.ipapi
from IPython import ColorANSI
from IPython.genutils import Term
from ipy_stock_completers import moduleCompletion

tc = ColorANSI.TermColors()

border  = '{yellow}'+"-"*80+'{normal}'
border  = border.format(yellow=tc.Yellow, normal=tc.Normal)
api_doc = border + """
 {red}Augmenting ipython namespace with the following:{normal}
  - the haystack registry @ ``hregistry`` is a dictionary like:
     :: ModelClass -> SearchIndexInstance
  - the api registry @ ``aregistry`` is a dictionary like:
     :: ModelClass.__name__.lower() -> ResourceInstance
  - all the conversion utilities bundled with medley api.  try listing them:
    >>> api.get_<tab>
  - misc (also available in lowercase versions):
    ``SolrAPICommonFieldIndex``
    ``MedleySearchQueryset``
    ``SearchQueryset``

 {red}Hints (try typing these lines):{normal}
  >>> aregistry['story']
  >>> hregistry[medleystory]
""".format(red=tc.Red, normal=tc.Normal) + border

medley_doc = border + """{red}
 Augmenting ipython namespace with the following:{normal}
   - every Model like medley.<app>.models.<Model>, available at <Model>.__name__
   - lowercase versions of the aforementioned are also permitted
   - a special value ``_model_dct``, which is a dictionary like:
     :: <Model>._meta.app_label -> [<Model>,..]

 {red}Hints (try typing these lines):{normal}
   >>> _model_dct | idump        # view it in sweet ncurses browser
   >>> MedleyS<tab>              # tab completion on model uppercase names
   >>> medleys<tab>              # tab completion on model uppercase names
   >>> medleystory.o.all()       # shortcut for ".objects"
""".format(red=tc.Red, normal=tc.Normal) + border

medley_admin_doc = border + """{red}
 Augmenting ipython namespace with the following:{normal}
   - a special value ``_admin_dct``, which is a dictionary like:
     :: <Model>._meta.app_label -> [<ModelAdmin>,..]

 {red}Hints (try typing these lines):{normal}
   >>> _admin_dct | idump        # view it in sweet ncurses browser
""".format(red=tc.Red, normal=tc.Normal) + border


import os
opj=os.path.join
from IPython.macro import Macro

def load_three_venv_macros():
    """ chains to three_venv_cmd()) """
    macro = Macro("__IPYTHON__.three('vm', _margv[0])")
    __IPYTHON__.shell.user_ns.update(dict(vm = macro))
    macro = Macro("__IPYTHON__.three('rs')")
    __IPYTHON__.shell.user_ns.update(dict(rs = macro))

    cmd  = '! cd ' + os.path.join(os.environ['VIRTUAL_ENV'],'src','storyville','solr')
    cmd += '; kill -KILL `cat solr.pid`; sleep 3'
    cmd += '; ./run-solr.sh& echo $!>solr.pid'
    __IPYTHON__.shell.user_ns.update(dict(solr = Macro(cmd)))
    __IPYTHON__.shell.user_ns.update(dict(review = Macro("three('review')")))

    def three_venv_cmd(*cmd):
        """ proxy to three_venv.sh """
        cmd = ' '.join(map(str, cmd))
        tmp = os.environ.get('CMG_LOCAL_VIRTUALENV_VERSION',None)
        if tmp:
            del os.environ['CMG_LOCAL_VIRTUALENV_VERSION']

        try:

            jd = os.environ['JD_DIR'] if 'JD_DIR' in os.environ else \
                 __IPYTHON__.user_ns['proj']._paths['jd']
            three_venv = os.path.join(jd, 'three_venv.sh')

            os.system('bash -c "source ' + three_venv + '; ' + cmd + '"')
        finally:
            if tmp:
                os.environ['CMG_LOCAL_VIRTUALENV_VERSION'] = tmp

    __IPYTHON__.shell.three = three_venv_cmd
    __IPYTHON__.shell.user_ns.update(three=three_venv_cmd)

def load_utest_macros():
    """ macro for utesting that features much better tab
        completion than bash: supports dotpaths as well
        as file-names.
    """
    dad_test = '!django-admin.py test ' + \
               '${getattr(_margv[0],"__name__",_margv[0])} ' + \
               '--settings=storyville.conf.utest_template ' + \
               '--noinput --verbosity=2'
    __IPYTHON__.shell.user_ns.update(dict(test=Macro(dad_test)))

class L(object):
    """ various lazy stuff.. some of this is experimental """

    @property
    def appcache(self):
        from django.db.models.loading import AppCache
        return AppCache()

    @property
    def apps(self):
        return self.appcache.get_apps()

    @property
    def app_dirs(self):
        files_or_dirs = [ os.path.splitext(a.__file__)[0] \
                          for a in self.apps ]
        files_or_dirs = [ fod.split(os.path.sep) \
                          for fod in files_or_dirs ]
        files_or_dirs = [ fod[:fod.index('models')] \
                          for fod in files_or_dirs ]
        dirs = [ os.path.sep.join(fod) \
                for fod in files_or_dirs ]
        return dirs

    @property
    def medley_app_dirs(self):
        return [ x for x in self.app_dirs \
                 if 'storyville/medley' in x ]

    @property
    def medley_tests_files(self):
        out=[]
        for x in self.medley_app_dirs:
            testdir = os.path.join(x,'tests')
            testfile = os.path.join(x,'tests.py')
            if os.path.exists(testdir):
                out.append(testdir)
            if os.path.exists(testfile):
                out.append(testfile)
        return out

    @property
    def medley_tests(self):
        from medley.util.testing import import_test_classes
        out = []
        for fod in self.medley_tests_files:
            out += import_test_classes(fod, None)
        out = set(out)
        return out

    @property
    def models(self):
        """ Helper to get all the models in a dictionary.
            NOTE: this triggers django autodiscovery, obv
        """
        return dict( [ [ m.__name__, m] \
                       for m in L.appcache.get_models() ] )
L = L()

from ipy_bonus_yeti import report

def load_medley_customizations2():
    """ post-activation instructions for medley-related
        environments.  these use os.environ and can't
        work until after a VENV is activated.
    """
    manager = __IPYTHON__.user_ns['proj']
    report.medley_customization("binding new subprojects: "
                                "medley-templates, storyville, ellington,")

    manager.bind(os.environ.get('JD_DIR','~/jellydoughnut'), 'jd')
    src_dir = opj(os.environ['VIRTUAL_ENV'], 'src')
    manager.bind(opj(src_dir, 'storyville',       'medley'),    'medley')
    manager.bind(opj(src_dir, 'ellington',        'ellington'), 'ellington')
    manager.bind(opj(src_dir, 'medley-templates', 'templates'), 'mtemplates')
    manager._ipy_install()
    report.medley_customization('loading three-venv macros')
    load_three_venv_macros()
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'storyville.conf.local'

    # set the DB port.  the 'activate' file has been modified by three_venv's create_environment
    # but activate.py was left untouched so we have to snag a value from the former file in
    # this fashion.  doing this is critical or you'll get FATAL: authorization blah blah errors
    # whenever you try to do anything with django.

    try:
        activate_file = os.path.join(os.environ['VIRTUAL_ENV'],'bin','activate')
        c = open(activate_file).readlines()
        port = [ line for line in c if 'CMG_DB_PORT' in line][0].strip().split('=')[1]
        os.environ['CMG_DB_PORT'] = port
    except Exception,e:
        report.medley_customization('error setting CMG_DB_PORT from ',activate_file)
    else:
        report.medley_customization('set CMG_DB_PORT='+port)



def load_medley_customizations():
    report.msh('installing medley support')
    __IPYTHON__.magic_alias('d dad')
    __IPYTHON__.magic_alias('ctest dad create_test_template '
                            '--settings=storyville.conf.utest_template')
    __IPYTHON__.shell.user_ns.update(engage=engage,)

    ip = IPython.ipapi.get()

    # django-specific
    def test_completer(self, event):
        """ """
        event = event.copy()
        line = event.line.split()
        line = line[line.index('test'):]
        event.line = ' '.join(['from'] + line[1:])
        print event.line
        event.command = 'from'
        return moduleCompletion(event.line)


    ip.set_hook('complete_command', test_completer, str_key = 'test')
    load_utest_macros()


class Engage(object):
    """ """
    @property
    def standard(self):
        # the usual suspects
        import medley
        import storyville
        import ellington
        from inspect import getfile
        self._update(dict(medley=medley,
                          getfile=getfile,
                          storyville=storyville,
                          ellington=ellington))

    @property
    def medley_models(self):
        """ """
        lst = [ [model.__name__, model] for _,model in L.models.items() \
                if model.__module__.startswith('medley') ]
        self._update(dict(lst))

        lst = map(lambda x: [x[0].lower(),x[1]],lst)
        self._update(dict(lst))

        map(lambda mdl: setattr(mdl,'o',mdl.objects),
            [x[1] for x in lst])

        apps = list(set([ tmp[1]._meta.app_label for tmp in lst]))
        the_test = lambda m: m._meta.app_label==app_label
        models_by_app = dict([ [app_label,
                                filter(the_test,
                                       [x[1] for x in lst])] \
                               for app_label in apps ])

        self._update(dict(_model_dct=models_by_app))

        print medley_doc

    @property
    def medley_admin(self):
        """
        """
        from django.contrib.admin import site, autodiscover;
        autodiscover()
        admins_by_app = {}
        for admin in site._registry.values():
            if admin.model.__module__.startswith('medley'):
                app = admin.model._meta.app_label
                if app in admins_by_app: admins_by_app[app] += [admin]
                else: admins_by_app[app] = [ admin ]
        self._update(dict(_admin_dct=admins_by_app))
        print medley_admin_doc

    def api(self):
        # argh, wtf! done because it prints twice! :/
        print api_doc

        # trigger some of the autodiscovery
        import medley.api.urls

        # triple-api import deprecated soon..
        try:
            from medley.api.api import api
        except ImportError:
            from medley.api.site import api
        from medley.extensions.search_indexes \
             import SolrAPICommonFieldIndex

        from haystack import site
        from medley.medley_search.query import MedleySearchQuerySet
        from medley.medley_search.query import SearchQuerySet
        hregistry = site._registry
        aregistry = api._registry
        ctx = dict(api=api,
                   hregistry=hregistry, aregistry=aregistry,
                   SolrAPICommonFieldIndex=SolrAPICommonFieldIndex,
                   MedleySearchQuerySet=MedleySearchQuerySet,
                   medleysearchqueryset=MedleySearchQuerySet,
                   SearchQuerySet=SearchQuerySet,
                   searchqueryset=SearchQuerySet,
                   )
        self._update(ctx)

    def _update(self, ctx):
        """ this actually effects the namespace mangling,
            overwriting anything that might already be
            there
        """
        __IPYTHON__.shell.user_ns.update(ctx)
engage = Engage()
