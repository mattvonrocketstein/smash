title: Project Management
menu-position: 5
---

##What is it?

**The project manager is a smash plugin that helps out with all kinds of project automation.**  Basically projects are natural abstractions for lots of kinds of work, and will be familiar to anyone who has used an IDE.  In smash, the concept is quite flexible and powerful for all sorts of automation.  **A project is defined by a nickname and associated with a directory.**  In the simplest case a project can function as merely a bookmark that can be jumped to, or for more involved projects you might want a set of command aliases and macros which other projects do not share.  Projects also have *types* and *operations*, which can either be specified or autodetected based on the contents of the project directory.

##Important concepts

**Project Types** are simply lists of strings, such as ["python"], or ["python", "puppet"].  The type of a project may be provided by the user or autodetected by smash.  New user-defined types are encouraged, but they won't have default operations (see below).

The default operations and some examples of what they might involve for your project are described below:

**Project Operations** are things you can do to projects, where the builtin operations are *add*, *activate*, *build*, *check*, *test*, and *deactivate*.  The meaning of an operation varies based on project-type, for instance testing a python project will be different than testing a ruby project.  User defined operations are also possible.  The specific implementation for a given operation can be specified per project as a list, where the list contains a sequence of shell commands or python callables.  If a given operation is not defined for a given project, a reasonable default for that operation should be guessed based on the project type.  For each operation, here are some examples of the type of actions you might like to perform:

* *Add*: register new project nickname & directory with the Project Manager
* *Activate*: pull fresh code, start project-specific database services or system daemons.
* *Build*: maybe tox for a python project, ant for java or whatever
* *Check*: verify symlinks, start linters or other static analysis
* *Test*: set environment variables and then run unittests
* *Deactivate*: push finished code, stop project-specific database services or other system daemons.

In the sections below, you will find instructions on how to invoke operations and what the default operations will involve for each project type.

##Project-manager Commands

<a id="cmd-add"></a>
**Adding Projects** can be accomplished temporarily with `add_project nickname dir`, or new projects can be permanently added in `~/.smash/config.py`.  If you have a single directory like *~/code* that contains multiple projects, you can turn each subdirectory into a project by setting `project_search_dir` in the smash config file.

-------------------------------------------------------------------------------

<a id="cmd-activate" href="#cmd-activate"></a>
**Activating Projects** is done with a command like `proj.nickname`.  (Note: you can use tab-completion over project names).

* Vagrant projects:
    * run "vagrant up"
* Python projects:
    * jump to the project base directory
    * if the project contains one or more virtualenvs, then
        * the most recent will be activated (.tox is ignored)

-------------------------------------------------------------------------------

<a href="#cmd-deactivate" id="cmd-deactivate"></a>
**Deactivating Projects** usually isn't necessary because activating a new project will automatically deactivate the previous project.  To manually deactivate the current project, type `proj._deactivate` or `deactivate_project`.

1. Vagrant projects:
    * run "vagrant halt"
2. Python projects:
    * deactivate virtual environments associated with project

-------------------------------------------------------------------------------


<a id="cmd-build" href="#cmd-build">**Building Projects**</a> is done for the current project using `.build`, or for an arbitrary project using `build_project nickname`.

* Python projects:
    * if tox.ini is present
        * runs `tox $TOX_BUILD_ARGS` *(set this up in the activation rules)*
    * if setup.py is present run "setup.py develop"
* Doc projects:
    * if there is a README.md markdown file, generate github style html
    * if there are other markdown files, generate html

-------------------------------------------------------------------------------

<a id="cmd-check" href="#cmd-check">**Checking Projects**</a> is done on the current project using `.check`, or on an arbitrary project using `check_project nickname`.

* Python projects:
    * `flake8` will be used if found, virtualenvs and tox will be ignored
    * collects statistics about total problems and triages files
* Haskell Projects:
    * `hlint` will be used if found
    * output is parsed for statistics about total problems


-------------------------------------------------------------------------------

<a id="cmd-test">**Testing Projects**</a> is done for the current project using `.test`, or on an arbitrary project `test_project nickname`.  It's difficult to guess in general how project tests should be run, but smash can detect or guess a few different patterns:
* Python projects:
    * try using tox first if tox.ini found
        * runs `tox $TOX_TEST_ARGS` *(set this in the activation rules)*
    * if tox is not found, look for `tests/` or `*/tests` folder,
        * if found, collect and attempt to run with pytest

-------------------------------------------------------------------------------

<a id="cmd-search">**Searching inside a project**</a> is blah blah blah blah blah.
* Python projects:
    * try using tox first if tox.ini found
        * runs `tox $TOX_TEST_ARGS` *(set this in the activation rules)*
    * if tox is not found, look for `tests/` or `*/tests` folder,
        * if found, collect and attempt to run with pytest
