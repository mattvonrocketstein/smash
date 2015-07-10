""" smashlib.env
"""
import os

from smashlib.ipy3x.core.magics.osm import OSMagics


class EnvMixin(object):

    """ EnvMixin provides env.json-reading
        support to the project manager
    """

    def _get_env_group(self, group_name):
        return self.env_map.get(group_name, [])

    def _load_env_group(self, group_name):
        tmp = self._get_env_group(group_name)
        for k, v in tmp:
            self.report("setting {0} {1}".format(k, v))
            OSMagics().set_env("{0} {1}".format(k, v), quiet=True)
        self.report("Loaded {0} env-vars".format(len(tmp)))

    def _unload_env_group(self, group_name):
        tmp = self._get_env_group(group_name)
        for k, v in tmp:
            del os.environ[k]