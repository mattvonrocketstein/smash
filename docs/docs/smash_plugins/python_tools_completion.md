<a id="ptc"></a>
### Plugin: Python Tools Completion

This plugin provides completion options for common python tools like [Fabric](#), [IPython](#), [setup.py](#), [flake8](#)/[pyflakes](#) [tox](#), and other stuff you probably use on a daily basis.  Completion for each command is at least over command line options/flags, but in some cases there are other context clues that can be provided:

* fabric completion also works over task names.
* tox completion includes available environments according to tox.ini when using "tox -e"
* ipython completion includes available profiles when using --profile option

#####Configuration Options:
