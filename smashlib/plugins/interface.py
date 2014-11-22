""" smashlib.plugins.interface
"""

class PluginInterface(object):
    def __repr__(self):
        return "plugin interface"

    __str__ = __repr__

    def __init__(self, smash):
        self.smash = smash

    @property
    def edit(self):
        self.smash.shell.run_cell('ed_config')

    @property
    def __doc__(self):
        self.update()

    def update(self):
        tmp = self.smash._installed_plugins
        def fxn(name):
            return self.smash._installed_plugins[name]
        for name in tmp:
            prop=property(lambda himself: fxn(name))
            setattr(self.__class__,name,prop)
        whitelist = ['edit','smash', 'update']
        for x in dir(self):
            if not x.startswith('_') and \
                   x not in tmp and \
                   x not in whitelist:
                raise ValueError("interface is not clean")
