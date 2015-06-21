title: Use Cases: Python
menu-position: 3
---

This section is just an overview.  You could also jump directly to the plugin documentation for the relevant plugins: [Python Tools Completion](plugins.html#ptc), [Python Virtual Environments](plugins.html#virtualenv), [Project Manager](project_manager.html)

<a id="smash-for-python-devs"></a>
####Smash is a python interpretter
Smash is a fundamentally just a wrapper on top of IPython.  You can expect everything console IPython does to work from smash without any trouble.

-------------------------------------------------------------------------------

####<a id="venvs">Python Virtualenv Support</a>
Smash has sophisticated virtualenv support which is useful particularly if you're working on multiple projects or working with multiple versions of the same requirements.  Activating/deactivating venvs is done with `venv_activate some_dir` and `venv_deactivate`, respectively.  This not only updates your $PATH, but updates the python runtime.  Modules from the new environment can now be imported directly, and side-effects from the old virtualenv are purged.  For more details take a look at the [plugin documentation](plugins.html#virtualenv).  To activate and deactivate virtualenv's automatically, take a look at the [project manager documentation](/project_manager.html).

-------------------------------------------------------------------------------

####<a id="macros">Macros</a>

Macros and command functions are similar to shell functions, meaning they are typically useful when you have in mind a piece of functionality that is: *(a)* more complex than an alias *(b)* interacting or sharing information with the shell itself, *(c)* too small or too idiosyncratic to merit it's own file in ~/bin.

Macros are an IPython concept, and simply correspond to a named array of input-lines (possibly python or possibly shell, anything that smash can take as input).  Macros run with no input and have no output, essentially they run on and may modify the current "environment", including python namespace, environment variables, whatever.  Macros can be built from a given sequence, a start-end range over the input history, or the contents of a file.  For more documentation on this, try typing `macro??` in your smash shell.

-------------------------------------------------------------------------------

####<a id="command-fxns">Command functions</a>

**Command-functions** are python functions which are parsed into something that's more conveniently called from the command line.  For instance suppose you have a python function like this:

~~~~{.python}
def check_mail(source):
    if source=='gmail':
        do_stuff()
    elif source=='work':
        do_other_stuff()
    else:
        error()
~~~~

Since smash is a python interpretter, there is already an obvious invocation: `check_mail(my_source)`.  However if the function is wrapped with a `@command_function` decorator, then we'll get a nice and more shell-like invocation where all the appropriate details of option parsing are determined automatically (see example below).  During the smash bootstrap, every python function declared in the file at `~/.smash/etc/commands.py` will automatically be wrapped as a command function, and use the config variable `load_commands_from` to specify any other files to load.

~~~~{.python}
$ command_function(check_mail)
$ check_mail --source=gmail
~~~~

-------------------------------------------------------------------------------

####<a id="completion">Completion Support for Python Tools</a>

By default smash supports various completion options for common python tools like [Fabric](#), [IPython](#), [setup.py](#), [flake8](#)/[pyflakes](#) [tox](#), and other stuff you probably use on a daily basis.  Some of this is just option completion, but some is more interesting and dynamic (for example completion of task-names with fabric).  For a full description, take a look at the [plugin documentation](plugins.html#python-tools-completion)

-------------------------------------------------------------------------------
