""" smashlib.patches.edit
"""
import re
from smashlib.patches.base import PatchMagic

r_file_and_line = re.compile('.+[:](\d+)[:]?(\d*)$')


class PatchEdit(PatchMagic):
    """ patches the builtin ipython edit magic so that filenames like
        "a/b/c:<row>:<col>" will be rewritten to use -n <lineno>, as
        ipython expects
    """
    name = 'edit'

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
