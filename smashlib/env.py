""" smashlib.env
"""
import os

class EnvMixin(object):
    """ EnvMixin provides env.json-reading
        support to the project manager
    """
    def _get_env_group(self, group_name):
        return self.env_map.get(group_name, [])

    def _load_env_group(self, group_name):
        tmp = self._get_env_group(group_name)
        for k,v in tmp:
            self.report("setting {0} {1}".format(k,v))
            self.smash.shell.magic("env {0} {1}".format(k,v))
        self.report("Loaded {0} env-vars".format(len(tmp)))

    def _unload_env_group(self, group_name):
        tmp = self._get_env_group(group_name)
        for k,v in tmp:
            del os.environ[k]
