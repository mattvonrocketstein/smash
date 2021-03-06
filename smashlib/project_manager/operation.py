""" smashlib.project_manager.operation

    base class for activation, deactivation, check, test, and build
"""
import os
from smashlib.plugins import Plugin


class OperationStep(Plugin):

    """ thin wrapper, basically a named lambda. """
    #verbose = True

    def __init__(self, name, fxn=None, pm=None, args=tuple(), ):
        self.project_manager = pm
        self.name = self.project_manager._current_project
        self.args = args
        self.callable = fxn
        assert callable(fxn)
        self.init_logger()

    def __call__(self):
        self.report(str(self))
        self.callable(*self.args)

    @property
    def operation_name(self):
        """ really dumb heuristic.. subclassers can just set this as a
            class property """
        return self.__class__.__name__.lower().replace('step', '')

    def __repr__(self):
        return '<{0}:{1}>'.format(
            self.__class__.__name__,
            self.name)
    __str__ = __repr__


class NullOperationStep(OperationStep):

    """ Activation step used when literally no
        other activation steps could be guessed at
    """

    def __init__(self, project_manager):
        self.project_manager = project_manager
        name = self.__call__.__name__
        _callable = lambda: \
            self.project_manager.report(
                'no project {0} steps are understood for "{1}"'.format(
                    self.operation_name, self.project_manager._current_project))
        super(NullOperationStep, self).__init__(
            name, _callable, pm=project_manager)


def require_active_project(fxn):
    def newf(project_manager, *args, **kargs):
        pname = project_manager._current_project
        if pname is None:
            project_manager.warning("You must activate a project first")
            return None
        else:
            pdir = project_manager.project_map[pname]
            if not os.path.exists(pdir):
                project_manager.warning(
                    "require that project dir should exist")
                return None
            else:
                return fxn(project_manager, *args, **kargs)
    return newf
