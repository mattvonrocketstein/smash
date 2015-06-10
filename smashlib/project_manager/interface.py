""" smashlib.project_manager.interface
"""
import os

from goulash.python import ope
from goulash.venv import find_venvs
from goulash._fabric import require_bin

def require_active_project(fxn):
    def newf(self, *args, **kargs):
        pname = self._project_manager._current_project
        if pname is None:
            self._project_manager.warning("You must activate a project first")
            return None
        else:
            return fxn(self, *args, **kargs)
    return newf

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
    @require_active_project
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
        patterns = ['*/.*/*']
        if ope(gitignore):
            with open(gitignore) as fhandle:
                patterns += [x.strip() for x in fhandle.readlines()]
        patterns = ' -and '.join( ['! -wholename "{0}"'.format(p) \
                                   for p in patterns ] )
        if patterns:
            patterns = '\\( {0} \\)'.format(patterns)
        sed = """| sed 's/[^[:space:]]\+ //';"""
        base_find = 'find {0} -type f {1}'.format(
            self._project_manager._project_dir, patterns)
        cmd = '{0} -printf "%T+ %p\n" | sort -n {1}'.format(base_find, sed)
        filenames = self._project_manager.smash.system(cmd, quiet=True)
        filenames = filenames.split('\n')
        filenames.reverse()
        return filenames[:10]

    @require_active_project
    def _search(self, *pat):
        """ example usage:

              smash$ .search foo|grep bar
              smash$ proj._search foo|grep bar
        """
        pat = ' '.join(pat)
        if '|' in pat:
            tmp = pat.split('|')
            pat = tmp.pop(0)
            post_process = '|'+'|'.join(tmp)#ie "| grep foo" or whatever
        else:
            post_process = ''
        require_bin('ack-grep')
        venvs = self._venvs
        cmd = 'ack-grep "{0}" "{1}" {2}'
        pdir = self._project_manager.project_map[
            self._project_manager._current_project]
        junk = venvs+['.tox']
        ignores = ['--ignore-dir="{0}"'.format(j) for j in junk]
        ignores = ' '.join(ignores)
        cmd = cmd.format(pat, pdir, ignores)
        cmd += post_process
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

    def __qmark__(self):
        pmap = self._project_manager.project_map
        out = ['ProjectManager: ({0} projects)'.format(len(pmap))]
        #out += ['   projects:']

        #    out += ['       : {0}'.format(nick)]
        cp = self._project_manager._current_project
        aliases = self._project_manager.alias_map
        if cp:
            out += ['   current_project: {0}'.format(cp)]

        if aliases:
            lst = [
                [group,len(cmds)] for group,cmds in \
                                             aliases.items()]
            out += ['   alias groupings: ']
            for g in lst:
                out+=['       : {0} (with {1} aliases)'.format(*g)]
        sdirs = self._project_manager.search_dirs
        if sdirs:
            out += ['   search_dirs:']
            for nick in sdirs:
                out += ['       : {0}'.format(nick)]
        return '\n'.join(out)
