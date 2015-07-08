""" smashlib.plugins.which
"""
from smashlib.plugins import Plugin
from smashlib.channels import C_REHASH_EVENT
from smashlib.util.events import receives_event

from goulash._os import summarize_fpath
from goulash._fabric import qlocal
from report import Reporter as R

report = R("which")


class EnhancedWhich(Plugin):

    verbose = True

    def init(self):
        self._install('fake_bus')

    def which(self, query):
        #system_result = self.smash.system('which {0}'.format(query)).strip()
        system_result = qlocal('which {0}'.format(query), capture=True).strip()
        try:
            python_result = __import__(query)  # sys.modules.get(query, None)
        except ImportError, e:
            #self.report("error importing: "+str(e))
            python_result = None
        if system_result:
            report.system('{0}'.format(system_result))
            finfo = qlocal('file "{0}"'.format(system_result), capture=True)
            finfo = finfo.strip()
            if finfo:
                finfo = ' '.join(finfo.split()[1:])
                report.system('  type: {0}'.format(finfo))
        if python_result:
            fpath = getattr(python_result, '__file__', '__builtin__')
            fpath = summarize_fpath(fpath)
            report.python('module: "{0}"'.format(python_result.__name__))
            report.python('\tfile: {0}'.format(fpath))
            version = getattr(python_result, '__version__',
                              getattr(python_result, 'VERSION', None))
            version = version or getattr(python_result, 'version', None)
            report.python('\tversion: {0}'.format(version or '??'))

    @receives_event(C_REHASH_EVENT, quiet=True)
    def _install(self):
        # any call to rehashx will reinstall the old alias,
        # so this has to undo some of rehashx's work
        try:
            self.smash.shell.alias_manager.undefine_alias('which')
        except ValueError:
            # no such alias is defined
            pass
        self.contribute_macro(
            'which',
            [
                "from smashlib import get_smash",
                "_smash = get_smash()",
                "himself = _smash._installed_plugins['which']",
                "tmp = _smash.shell._last_input_line",
                "himself.which(tmp.split()[-1])",
                #"print tmp.split()[-1]"
            ])


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    return EnhancedWhich(ip)


def unload_ipython_extension(ip):
    pass
