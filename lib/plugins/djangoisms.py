""" djangoisms:

      a smash plugin for supporting various django stuffs
"""
import os

from smashlib.projects import Project, COMMAND_NAME
from smashlib.util import opj, ope, report, post_hook_for_magic
from smashlib.smash_plugin import SmashPlugin

def set_settings(dsm):
    os.environ['DJANGO_SETTINGS_MODULE'] = dsm

class D(object):
    """ lazy django stuff.

        you can't mess around with this until
        SETTINGS_MODULE is set in os.environ
    """
    @property
    def apps(self):
        from django.db.models.loading import AppCache
        appcache = AppCache()
        return appcache.get_apps()
    @property
    def models(self):
        """ Helper to get all the models in a dictionary.
            NOTE: this triggers django autodiscovery, obv
        """
        from django.db.models.loading import AppCache
        appcache = AppCache()
        return dict( [ [ m.__name__, m] \
                       for m in appcache.get_models() ] )

    @property
    def app_dirs(self):
        from smashlib.active_plugins import djangoisms
        apps=D().apps
        files_or_dirs = [ os.path.splitext(a.__file__)[0] \
                          for a in apps ]
        files_or_dirs = [ fod.split(os.path.sep) \
                          for fod in files_or_dirs ]
        files_or_dirs = [ fod[:fod.index('models')] \
                          for fod in files_or_dirs ]
        dirs = [ os.path.sep.join(fod) \
                for fod in files_or_dirs ]
        return dirs

def update_models():
    """ find all the models in INSTALLED_APPS,
        inject them and their lowercase equivalents
        into the IPython namespace
    """

def look_for_project(_dir=None):
    """ returns True if dir looks like a django project """
    _dir = _dir or os.getcwd()
    if all([ope(opj(_dir, 'settings.py')),]):
        return True
    return False

def look_for_app(_dir=None):
    """ returns True if dir looks like a django app"""
    _dir = _dir or os.getcwd()
    if all([ope(opj(_dir, 'urls.py')),
            ope(opj(_dir, 'models.py'))]):
        return True
    return False

class Plugin(SmashPlugin):
    requires = []
    report = report.bookmark_plugin

    def install(self):
        #self.contribute('update_models',update_models)
        post_hook_for_magic('cd', look_for_app)
