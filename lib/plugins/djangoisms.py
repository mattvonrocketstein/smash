"""

from django.contrib.sites.models import Site
ajc=Site.objects.filter(domain='www.ajc.com')
x.objects.random()
"""
import os
opj=os.path.join
ope=os.path.exists

from smashlib.projects import Project, COMMAND_NAME
from smashlib.util import report, post_hook_for_magic
from smashlib.plugins import SmashPlugin

def update_models():
    """ find all the models in INSTALLED_APPS,
        inject them and their lowercase equivalents
        into the IPython namespace
    """
def look_for_app():
    cwd=os.getcwd()
    if all([ope(opj(cwd,'urls.py')),
            ope(opj(cwd,'models.py'))]):
        report.django_magic('detected a django app')

class Plugin(SmashPlugin):
    requires = []
    report = report.bookmark_plugin

    def install(self):
        #self.contribute('update_models',update_models)
        post_hook_for_magic('cd', look_for_app)
