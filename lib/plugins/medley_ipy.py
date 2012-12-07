""" medley_ipy
"""

import os, sys

from IPython import ColorANSI
from IPython.macro import Macro
from smashlib.util import report
from smashlib.plugins import SmashPlugin

opj = os.path.join
tc  = ColorANSI.TermColors()

usage = """
Hybrid IPython / bash environment tailored for medley development.
  1) IPython extensions:

    project manager:

      >>> proj.medley      # cd to src/storyville/medley
      >>> proj.ellington   # cd to src/storyville/ellington
      >>> proj.mtemplates  # cd to src/storyville/medley-templates

    shortcuts in webrowser (you can find more using tab completion):

      # opens up hudson's login window in a new tab
      >>> show.hudson.login

      # opens up munin's celery graphs for FE-5
      >>> show.munin.celery._5
"""

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


class L(object):
    """ various lazy stuff.. some of this is experimental """

    @property
    def apps(self):
        from django.db.models.loading import AppCache
        appcache = AppCache()
        return appcache.get_apps()

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
        from django.db.models.loading import AppCache
        appcache = AppCache()
        return dict( [ [ m.__name__, m] \
                       for m in appcache.get_models() ] )
L = L()


def load_medley_customizations2():
    """ post-activation instructions for medley-related
        environments.  these use os.environ and can't
        work until after a VENV is activated.
    """
    from smashlib import PROJECTS as proj
    src_dir = opj(os.environ['VIRTUAL_ENV'], 'src')
    storyville_dir = opj(src_dir, 'storyville')
    sys.path.append(storyville_dir)
    report.medley_customization('loading three-venv macros')
    plugin = SmashPlugin()
    plugin.contribute('vm',
                      Macro("__IPYTHON__.three('vm', _margv[0])"))
    plugin.contribute('rs', Macro("__IPYTHON__.three('rs')"))
    plugin.contribute('review', Macro("__IPYTHON__.three('review')"))
    cmd  = '! cd ' + os.path.join(os.environ['VIRTUAL_ENV'],'src','storyville','solr')
    cmd += '; kill -KILL `cat solr.pid`; sleep 3'
    cmd += '; ./run-solr.sh& echo $!>solr.pid'
    plugin.contribute('solr',  Macro(cmd))

    def three_venv_cmd(*cmd):
        """ proxy to three_venv.sh """
        cmd = ' '.join(map(str, cmd))
        tmp = os.environ.get('CMG_LOCAL_VIRTUALENV_VERSION',None)
        if tmp:
            del os.environ['CMG_LOCAL_VIRTUALENV_VERSION']
        try:
            jd = os.environ['JD_DIR'] if 'JD_DIR' in os.environ else \
                 __IPYTHON__.user_ns['proj']._paths['jellydoughnut']
            three_venv = os.path.join(jd, 'three_venv.sh')

            os.system('bash -c "source ' + three_venv + '; ' + cmd + '"')
        finally:
            if tmp:
                os.environ['CMG_LOCAL_VIRTUALENV_VERSION'] = tmp

    __IPYTHON__.shell.three = three_venv_cmd
    plugin.contribute('three', three_venv_cmd)

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

    report.medleys_customization('faking CMG_LOCAL_VENV_VERSION')
    report.medleys_customization('modding settings.DATABASES[default][port]]')
    from django.conf import settings
    settings.DATABASES['default']['PORT'] = port
    os.environ['CMG_LOCAL_VENV_VERSION'] = '1'

class Plugin(SmashPlugin):

    def install(self):
        """ fixme: none of this will be uninstalled.. """
        def jira(*args):
            import webbrowser
            page = 'https://jira.cmgdigital.com/browse/{0}'.format(*args)
            webbrowser.open_new_tab(page)
            return page
        self.contribute_magic('jira', jira)

        from smashlib import ALIASES as aliases
        report.msh('installing medley support')
        aliases.add('d dad', '__medley__')
        ctest=('ctest dad create_test_template '
               '--settings=storyville.conf.utest_template')
        aliases.add(ctest,'__medley__')
        self.contribute('engage', Engage())
        dad_test = '!django-admin.py test ' + \
                   '${getattr(_margv[0],"__name__",_margv[0])} ' + \
                   '--settings=storyville.conf.utest_template ' + \
                   '--noinput --verbosity=2'
        self.contribute('test', Macro(dad_test))

def load_medley_customizations(): Plugin().install()

class Engage(object):
    """ """
    @property
    def medley_models(self):
        """ """
        def reindex_it(self):
            "in master one day.."
            from medley.ellington_overrides.search.tasks import HaystackUpdateTask
            h = HaystackUpdateTask()
            h.taskfunc(self.__class__, pk_list=[self.id])

        plugin = SmashPlugin()
        for _, model in L.models.items():
            if model.__module__.startswith('medley'):
                plugin.contribute(model.__name__, model)
                plugin.contribute(model.__name__.lower(), model)
                setattr(model, 'o', model.objects)
                setattr(model, 'reindex',
                        lambda self: reindex_it(self))

        from django.contrib.sites.models import Site
        plugin.contribute('site', Site)
        plugin.contribute('Site', Site)
        print medley_doc

    @property
    def medley_admin(self):
        """ """
        plugin = SmashPlugin()
        from django.contrib.admin import site, autodiscover;
        autodiscover()
        admins_by_app = {}
        for admin in site._registry.values():
            if admin.model.__module__.startswith('medley'):
                app = admin.model._meta.app_label
                if app in admins_by_app: admins_by_app[app] += [admin]
                else: admins_by_app[app] = [ admin ]
        plugin.contribute('_admin_dct',admins_by_app)
        print medley_admin_doc

    @property
    def api(self):
        plugin = SmashPlugin()
        print api_doc

        # trigger some of the autodiscovery
        import medley.api.urls

        plugin.ifloat_names(['haystack.models.SearchResult',
                             'medley.medley_search.query.MedleySearchQuerySet',
                             'medley.medley_search.query.SearchQuerySet',
                             'medley.extensions.search_indexes.SolrAPICommonFieldIndex'])

        from medley.util.testing import RequestFactory
        plugin.contribute('requestfactory', RequestFactory())

        # triple-api import deprecated soon..
        try:
            api = plugin.float_name('medley.api.api.api')
        except:
            api = plugin.float_name('medley.api.site.api')
        plugin.contribute('api',api)
        plugin.contribute('hregistry', api.model_map)
        plugin.contribute('aregistry',api._registry)
