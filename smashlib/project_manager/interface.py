""" smashlib.project_manager.interface
"""
import os

from goulash.venv import find_venvs

class ProjectManagerInterface(object):
    """ This object should be a singleton and will be assigned to
        that main namespace as "proj".  In addition to the methods
        you see below, The ProjectManager extension
        will dynamically add/remove properties on to this
    """
    _project_manager = None

    @property
    def _type(self):
        return self._project_manager.guess_project_type(
            self._project_manager._current_project)

    @property
    def _venvs(self):
        pname = self._project_manager._current_project
        return find_venvs(
            self._project_manager.project_map[pname])

    @property
    def _recent(self):
        """ return a list of the top 10 most recently changed files in the
            current project's directory, where list[0] was changed most
            recently.  this automatically takes into account ignoring dotfiles
            and .gitignore contents.
        """
        gitignore = os.path.join(
            self._project_manager._project_dir,
            '.gitignore')
        from smashlib.python import ope
        patterns = ['*/.*/*']
        if ope(gitignore):
            with open(gitignore) as fhandle:
                patterns += [x.strip() for x in fhandle.readlines()]
        patterns = ' -and '.join( ['! -wholename "{0}"'.format(p) \
                                   for p in patterns ] )
        if patterns:
            patterns = '\\( {0} \\)'.format(patterns)
        # find . -type f \( -iname "*.c" -or -iname "*.asm" \)
        sed = """| sed 's/[^[:space:]]\+ //';"""
        base_find = 'find {0} -type f {1}'.format(
            self._project_manager._project_dir, patterns)
        cmd = '{0} -printf "%T+ %p\n" | sort -n {1}'.format(base_find, sed)
        filenames = self._project_manager.smash.system(cmd, quiet=True)
        filenames = filenames.split('\n')
        filenames.reverse()
        return filenames[:10]

    def _ack(self, pat):
        """ TODO: should really be some kind of magic """
        from smashlib.util._fabric import require_bin
        require_bin('ack-grep')
        venvs = self._venvs
        cmd = 'ack-grep "{0}" "{1}" {2}'
        pdir = self._project_manager.project_map[
            self._project_manager._current_project]
        ignores = ['--ignore-dir="{0}"'.format(venv) for venv in venvs]
        ignores = ' '.join(ignores)
        cmd = cmd.format(pat, pdir, ignores)
        results = self._project_manager.smash.system(cmd)
        print results

    @property
    def _check(self):
        pm = self._project_manager
        project_name = pm._current_project
        pm.check(project_name)

    @property
    def _test(self):
        pm = self._project_manager
        project_name = pm._current_project
        pm.test(project_name)