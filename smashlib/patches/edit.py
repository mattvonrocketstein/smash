""" smashlib.patches.edit
"""
import re
from IPython.core.magics.code import CodeMagics
from .base import PatchMagic

r_file_and_line = re.compile('.+[:](\d+)[:]?(\d*)$')


class PatchEdit(PatchMagic):
    """ patches the builtin ipython cd magic so that a post-dir-change
        event can be sent to anyone who wants to subscribe, and so that
        the "cd" command is quiet by default.
    """
    name = 'edit'
    original2 = staticmethod(CodeMagics._find_edit_target)


    def install(self):
        super(PatchEdit,self).install()

    def __call__(self, parameter_s='',last_call=['','']):
        opts, args = self.original.im_self.parse_options(parameter_s,'prxn:')
        fname = args
        lineno = ''
        if r_file_and_line.match(fname):
            lineno = '-n {0}'.format(fname.split(':')[1])
            fname = fname.split(':')[0]
        parameter_s = '{0} {1} {2}'.format('-x',lineno,fname)
        self.component.report('rewrote arguments going to edit: '+parameter_s)
        return self.original(parameter_s=parameter_s, last_call=last_call)
