""" ipy_project_manager

    abstractions for project management
 """

import os
import demjson

from smash.util import report
#from smash.venv import VenvMixin
from smash.python import opd, opj
from smash.plugins import SmashPlugin
from smash.util import post_hook_for_magic
from smash.projects import Project, ROOT_PROJECT_NAME

CONFIG_FILE_NAME = 'projects.json'


class Plugin(SmashPlugin):
    def install(self):
        config_file = opj(opd(opd(__file__)), CONFIG_FILE_NAME)
        Project._config_file = config_file
        report.project_manager('loading config: ' + config_file)
        if not os.path.exists(config_file):
            config = {}
            report.project_manager(' file does not exist')
        else:
            config = demjson.decode(open(config_file,'r').read())
            report.project_manager(' config keys: '+str(config.keys()))
        manager = Project(ROOT_PROJECT_NAME)

        # dont move this next line.  post_activate/post_invoke things might want the manager.
        __IPYTHON__.shell.user_ns['proj'] = manager

        manager._config = config
        instructions = config.get('instructions', [])
        # consider every directory in ~/code to be a "project"
        # by default proj.<dir-name> simply changes into that
        for method_name, args, kargs in instructions:
            getattr(manager, method_name)(*args, **kargs)

        # add option parsing for project-manager
        from smash.parser import SmashParser
        SmashParser.defer_option(args=('-p', "--project",),
                                       kargs=dict(
                                           dest="project", default='',
                                           help="specify a project to initialize", ),
                                       handler = lambda opts: getattr(manager,
                                                                      opts.project).activate)

        # per-project aliases
        default_aliases = config.get('aliases', {}).get(ROOT_PROJECT_NAME, [])
        from smash import aliases
        default_aliases = [ aliases.add(alias) for alias in default_aliases ]
        report.project_manager('adding aliases: ' + str(default_aliases))
        aliases.install()

        #raise Exception, aliases
        # install hooks in the environment
        # FIXME: this stopped working
        post_hook_for_magic('cd', manager._announce_if_project)

        __IPYTHON__.hooks['shutdown_hook'].add(lambda: manager.shutdown())
        __IPYTHON__.hooks['pre_prompt_hook'].add(manager.check)
