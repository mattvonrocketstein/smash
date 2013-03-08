""" api_helper
"""
import urllib
import demjson
from smashlib.python import opj, ope
from smashlib.util import read_config
from smashlib.smash_plugin import SmashPlugin

def get_data(url):
    data = urllib.urlopen(url).read()
    return demjson.decode(data)

class API(object):
    @property
    def _config(self):
        if ope(self._config_file):
            return read_config(self._config_file)
        else:
            report.ERROR('could not load configuration for the API plugin.')
            report.ERROR('  fix this or disable the plugin.')
            return {}

    def _populate(self):
        for x in self._config:
            func = lambda *args: get_data(self._config[x].format(*args))
            func.__doc__ = self._config[x]
            setattr(self,x,func)
    @property
    def _config_file(self):
        return opj(smashlib._meta['config_dir'], 'APIs.json')

    @property
    def __doc__(self):
        return ('This is the API-helper.\n'
                'config-file @ '+str(self._config_file)+'\n\n'
                )+str(self.config)

class Plugin(SmashPlugin):
    def install(self):
        api = API()
        api._populate()
        self.contribute('api', api)
