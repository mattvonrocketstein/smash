""" project_manager

    abstractions for project management
 """

import os
import demjson

from smashlib.util import report
from smashlib.python import opd, opj
from smashlib.plugins import SmashPlugin
from smashlib.util import post_hook_for_magic
from smashlib.projects import Project, ROOT_PROJECT_NAME, COMMAND_NAME

CONFIG_FILE_NAME = 'projects.json'

class Plugin(SmashPlugin):

    @staticmethod
    def load_instructions(manager, config):
        """ load instructions from json..

            these typically represent function-calls to bind() and bind_all()
        """
        instructions = config.get('instructions', [])
        for method_name, args, kargs in instructions:
            getattr(manager, method_name)(*args, **kargs)

    @staticmethod
    def load_aliases(config):
        default_aliases = config.get('aliases', {}).get(ROOT_PROJECT_NAME, [])
        from smashlib import aliases
        default_aliases = [ aliases.add(alias) for alias in default_aliases ]
        report.project_manager('adding aliases: ' + str(default_aliases))
        aliases.install()

    def ethandler_file_post_change(self, project_name, event_config):
        for file_extension, extension_handler_list in event_config.items():
            assert isinstance(extension_handler_list, list),extension_handler_list
            report.watchdog('would have built watchdog for {0}, handling {1} with {2}'.format(
                project_name,file_extension,extension_handler_list))

    def install(self):
        import smashlib
        config_file = opj(smashlib.config_dir, CONFIG_FILE_NAME)
        Project._config_file = config_file
        report.project_manager('loading config: ' + config_file)
        if not os.path.exists(config_file):
            config = {}
            report.project_manager(' file does not exist')
        else:
            config = demjson.decode(open(config_file, 'r').read())
            report.project_manager(' config keys: '+str(config.keys()))
        manager = Project(ROOT_PROJECT_NAME)

        # dont move this next line.  post_activate/post_invoke things might want the manager.
        __IPYTHON__.shell.user_ns[COMMAND_NAME] = manager

        manager._config = config
        for name, val in config.get('post_activate', {}).items():
            manager._add_post_activate(name, val)


        KNOWN_EVENT_TYPES = 'file-post-change'.split()
        for project_name,watchdog_config in config.get('watchdog', {}).items():
            assert isinstance(watchdog_config, dict), 'expected dictionary for wd-config@' + project_name
            for event_type, event_config in watchdog_config.items():
                assert event_type in KNOWN_EVENT_TYPES, 'unknown eventtype'
                event_type_handler = getattr(self, 'ethandler_' + event_type.replace('-','_'))
                event_type_handler(project_name, event_config)

        self.load_instructions(manager, config)

        # add option parsing for project-manager
        from smashlib.parser import SmashParser
        SmashParser.defer_option(args=('-p', "--project",),
                                       kargs=dict(
                                           dest="project", default='',
                                           help="specify a project to initialize", ),
                                       handler = lambda opts: getattr(manager,
                                                                      opts.project).activate)

        # per-project aliases
        self.load_aliases(config)

        # install hooks in the environment
        # FIXME: this stopped working
        post_hook_for_magic('cd', manager._announce_if_project)

        __IPYTHON__.hooks['shutdown_hook'].add(lambda: manager.shutdown())
        __IPYTHON__.hooks['pre_prompt_hook'].add(manager.check)