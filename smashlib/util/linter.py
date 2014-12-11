""" smashlib.util.linter
"""
import os
import re
from collections import defaultdict

from goulash.venv import find_venvs
from IPython.config.configurable import Configurable
from IPython.utils.traitlets import Bool, List

from smashlib.util._fabric import require_bin
from smashlib.v2 import Reporter

r_pep8_error = re.compile('.* E\d\d\d .*')

class Linter(Reporter):
    """ """
    def __init__(self, config, cmd_exec=None):
        if cmd_exec==None:
            cmd_exec=os.system
        self.cmd_exec = cmd_exec
        Configurable.__init__(self, config=config)
        self.init_logger()

    def __call__(self, _dir):
        raise Exception("abstract")

class HaskellLinter(Linter):
    verbose = True
    def __call__(self, _dir):
        self.report('starting')
        require_bin('hlint')
        base_cmd = 'cd {0} && hlint -c {0}'
        cmd = base_cmd.format(_dir)
        output = self.cmd_exec(cmd)
        lines = [x for x in output.split('\n') if x.strip()]
        total_problems = lines[-1].split()[0]
        #self.report("top files: {0}".))
        print output
        self.report("total problems: {0}".format(total_problems))

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
            always_ignore_names = [x for x in self.ignore_undefined_names \
                                   if isinstance(x, basestring) ]
            patterns = []
            res = re.compile(".*F821 undefined name '(" + \
                             '|'.join(always_ignore_names) + \
                             ")'")
            patterns.append(res)
            sometimes_ignore_names = [ x for x in self.ignore_undefined_names \
                                       if not isinstance(x, basestring) ]
            for name, pattern in sometimes_ignore_names:
                res2  = re.compile(pattern + ".*F821 undefined name '" + name + "'")
                patterns.append(res2)
            output_lines = filter(lambda x: not any([y.match(x) for y in patterns]), output_lines)
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
        total_problems = sum(report.values())
        self.report("total problems: {0}".format(total_problems))
        self.report("top files: {0}".format(dict(top)))
        return report.keys()
