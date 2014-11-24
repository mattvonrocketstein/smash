""" smashlib.util.linter
"""
import os

from collections import defaultdict
from IPython.config.configurable import Configurable
from IPython.utils.traitlets import Bool, List

from goulash.venv import find_venvs
from smashlib.util._fabric import require_bin
from smashlib.v2 import Reporter
import re
class Linter(Reporter):
    """ """
    def __init__(self, config, cmd_exec=None):
        if cmd_exec==None:
            cmd_exec=os.system
        self.cmd_exec = cmd_exec
        Configurable.__init__(self, config=config)
        self.init_logger()

    def __call__(self):
        raise Exception("abstract")

r_pep8_error = re.compile('.* E\d\d\d .*')

class PyLinter(Linter):
    ignore_unused_imports_in_init_files = True
    ignore_pep8 = Bool(False, config=True)
    ignore_undefined_names = List([], config=True)

    def __call__(self, _dir):
        require_bin('flake8')
        ignore = [
            'E501', # line-too-long
            ]
        base_cmd = 'cd {0} && flake8 {0}'
        cmd = base_cmd
        exclude = ['*build/*']
        for venv_dir in find_venvs(_dir):
            exclude.append(venv_dir)
        ignore = ','.join(ignore)
        exclude = ','.join(exclude)
        exclude = ' --exclude='+exclude
        ignore = ' --ignore='+ignore
        cmd = cmd.format(_dir) +  exclude
        output = self.cmd_exec(cmd)
        output_lines = output.split('\n')
        if self.ignore_pep8:
            output_lines = filter(
                lambda x: not r_pep8_error.match(x), output_lines)
            output= '\n'.join(output_lines)
        if self.ignore_unused_imports_in_init_files:
            r2 = re.compile('.*__init__.py.* F401 .*')
            output_lines = filter(lambda x: not r2.match(x), output_lines)
            output= '\n'.join(output_lines)
        if self.ignore_undefined_names:
            #raise Exception,self.ignore_undefined_names
            res = re.compile(".*F821 undefined name '(" + \
                             '|'.join(self.ignore_undefined_names) + \
                             ")'")
            output_lines = filter(lambda x: not res.match(x), output_lines)
            output= '\n'.join(output_lines)
        bad_files = [x.split(':')[0] for x in output_lines]
        err_counter = defaultdict(lambda:0)
        for x in bad_files:
            err_counter[x] += 1
        # sort files by number of errors
        sorted_by_severity = sorted(err_counter.items(), key=lambda x:-x[1])
        top = sorted_by_severity[:3]
        report = dict(sorted_by_severity)
        print output
        self.report("total problems: {0}".format(sum(report.values())))
        self.report("top files: {0}".format(dict(top)))
        return report.keys()