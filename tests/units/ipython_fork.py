"""
    To run this:
      python tests/ipython_fork.py IPython.core

    Running as above:
      Ran 422 tests in 5.124s
      FAILED (SKIP=11, errors=14, failures=4)

    Running from IPython source directory:
      Ran 481 tests in 10.947s
      OK (SKIP=12)

"""
import os
from smashlib.import_hooks import hijack_ipython_module
if __name__=='__main__':
    hijack_ipython_module()
    test_home = os.path.dirname(__file__)
    src_root = os.path.dirname(test_home)
    iptest = os.path.join(src_root, 'smashlib', 'ipy3x', 'testing', 'iptest.py')
    execfile(iptest)
