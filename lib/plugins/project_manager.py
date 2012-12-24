""" project_manager

    abstractions for project management
 """

import os
import demjson


from smashlib.util import die, read_config
from smashlib.util import report, list2table, bus
from smashlib.python import opd, opj, ope
from smashlib.smash_plugin import SmashPlugin
from smashlib.util import post_hook_for_magic, add_shutdown_hook
from smashlib.projects import Project, ROOT_PROJECT_NAME, COMMAND_NAME

CONFIG_FILE_NAME = 'projects.json'


class CurrentProject(object):
    """ """
    @property
    def wd(self):
        return os.getcwd()

    @property
    def _aliases(self):
        from smashlib import ALIASES as aliases
        return aliases

    @property
    def __doc__(self):
        from smashlib import PROJECTS as proj
        current_project = proj.CURRENT_PROJECT
        header, dat = proj._doc_helper([current_project])
        out = "This Project:\n\n{0}".format(list2table(dat, header=header))
        header = 'group shortcut command '.split()
        dat = []
        for alias in self._aliases:
            group = alias.affiliation
            shortcut = alias.alias.split()[0]
            cmd = ' '.join(alias.alias.split()[1:])
            if len(cmd) > 25:
                cmd=cmd.strip()[:25]+' ..'
            dat.append([group,shortcut,cmd])

        out+= "\n\nProject Aliases:\n\n{0}".format(list2table(dat, header=header))
        return out



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
        """ this only loads default aliases.  everything else is handled on activation """
        default_aliases = config.get('aliases', {}).get(ROOT_PROJECT_NAME, [])
        from smashlib import ALIASES as aliases
        default_aliases = [ aliases.add(alias) for alias in default_aliases ]
        #report.project_manager('adding aliases: ' + str(default_aliases))
        aliases.install()
    @property
    def config_filename(self):
        import smashlib
        return opj(smashlib._meta['config_dir'], CONFIG_FILE_NAME)

    def install(self):
        config_file = self.config_filename
        Project._config_file = config_file
        report.project_manager('loading config: ' + config_file)
        config = read_config(config_file)
        manager = Project(ROOT_PROJECT_NAME)

        # dont move this next line.  post_activate/post_invoke things might want the manager.
        self.contribute(COMMAND_NAME, manager)

        manager._config = config
        for name, val in config.get('post_activate', {}).items():
            bus().subscribe('post_activate.' + name, val)
        self.load_instructions(manager, config)
        self.load_aliases(config)
        post_hook_for_magic('cd', manager._announce_if_project)

        add_shutdown_hook(lambda: manager.shutdown())
        smashlib.PROJECTS = manager
        self.contribute('this',CurrentProject())

        self._add_option_parsing(manager)

    def cmdline_activate_project(self, opts):
        ('specify a project to inialize.\n'
         '(the project should already be recognized '
         'by the project manager)')
        project = getattr(manager, opts.project, None)
        if project is None:
            report("nonexistant project: {0}".format(opts.project))
            die()
        manager._activate(project)
    def _add_option_parsing(self, manager):
        # add option parsing for project-manager
        from smashlib.parser import SmashParser
        SmashParser.defer_option(args=('-p', "--project",),
                                       kargs=dict(
                                           dest="project", default='',
                                           help=self.cmdline_activate_project.__doc__ ),
                                 handler=self.cmdline_activate_project)
