**Under Construction: porting to IPython==3.0.0-dev**



[quickstart](#quickstart) | [overview](#overview)


<a name="about"/>
ABOUT
=====
SmaSh is the smart-shell.  It offers features for project management, a flexible plugin architecture that is easy to use, and simple configuration files that try to be as sane as possible.  [Python developers](#smash-for-python-devs) will be particularly interested because it also happens to be a python/bash hybrid which builds on the pysh profile for IPython.  It leverages all existing system [tab completion](#tab-completion) setup, apart from IPython completion in python namespaces.  It builds on, and offers very sophisticated support for python virtual environments.

<a name="quickstart"/>
QUICKSTART
==========

The smash installation happens in a sandbox, does not require root, and will not interefere with existing versions of IPython.  The cost of this is that setup is a little bit nonstandard and `setup.py` should not be used directly unless you only want to develop against the support libraries (for that see: [dev installation](#dev-installation))



```shell
  $ sudo apt-get install git-core python-virtualenv python-dev
  $ bootstrap=https://raw.githubusercontent.com/mattvonrocketstein/smash/master/bootstrap.sh
  $ curl $bootstrap | bash
  $ ~/bin/smash
```

<a name="philosophy"/>
PHILOSOPHY
==========

So, *why build yet another shell?*  Put simply, shells still kind of suck.  The main problem is that classic shells are inflexible and not easy to extend.  If you do manage to extend them, you probably had to do it with shell code, and so the result is something that's fragile and difficult to maintain.  Just for the sake of an example, let's consider the problem of a "do what I mean" extension for your shell, where if you type something that looks like a url then the url is opened automatically for you.  To effect a pre-exec style hook in bash, you'll have to do [black magic](http://www.twistedmatrix.com/users/glyph/preexec.bash.txt) with the `DEBUG` trap (ugh).  Zsh is better, but of course you'll still be writing (or at least invoking) your hooks in shell code.  This works at first, but things start to get messy when issues of code-reuse come up, or if you want to [invoke hooks conditionally](#pm), etc, etc.

SmaSh's close integration with python itself is a huge plus, but it's also just a side effect of fixing the main problems around making a shell that is truly flexible and nontrivially extensible.

<a name="overview"/>
FEATURE OVERVIEW
================


####Standard System Shell + Python Support
SmaSh functions seamlessly as a normal system shell, but it also a full fledged python interpretter.  It does shell stuff in the shell places, and python stuff in the python places.

![screenshot1](/docs/screenshots/demo-python-bash.png?raw=true "screenshot1")

If you're a bash user or an ipython user, your existing configuration efforts can also be [inherited automatically](#TODO-config-inheritance).  If you don't care anything about python, you can ignore that aspect of the shell completely.  If you *are* a python programmer, you probably spend as much time in a python interpretter as you do in shell.  You can trade those two windows for one to reduce screen clutter, as well as enjoy all the [other python friendly features of smash](#smash-for-python-devs).

-------------------------------------------------------------------------------

<a name="prompts"/>
####Prompts
By default smash ships with the wonderfully dynamic [liquidprompt tool](#https://github.com/nojhan/liquidprompt).  Liquidprompt has rich options for configuration and it's recommended that you [configure it in the normal way](https://github.com/nojhan/liquidprompt#features-configuration), but, some of these options can be overridden from `~/.smash/config.py`.  The default liquidprompt configuration features a prompt that shows activated python virtual environments, as well as VCS branch and commit/stash status, etc.  Other options include everything from cpu/battery status to write-permissions for the current directory.  Take a look at how it updates below based on the context:

![screenshot1](/docs/screenshots/demo-liquidprompt.png?raw=true "screenshot1")

-------------------------------------------------------------------------------

<a name="tab-completion"/>
####Tab-completion system
Depending on the context, tab completion information is derived either from ipython (for python namespaces, ipython aliases, etc) or directly from the system shell (for system commands, VCS subcommands, debian packages, whatever).  A few observations about this setup:

1. the smash completion system is at least as robust as your system shell
2. complete support for IPython's invaluable completion/readline facilities
3. you have choices now when writing new completers: ipython way or the shell way

-------------------------------------------------------------------------------

<a name="smash-for-python-devs"/>
SMASH FOR PYTHON DEVS
=====================

####Python Virtualenv Support
SmaSh has sophisticated virtualenv support which useful particularly if you're working on multiple projects or working with multiple major versions of the same software.  Activating/deactivating venvs is done with `venv_activate some_dir` and `venv_deactivate`, respectively.  This not only updates your $PATH, but updates the python runtime.  Modules from the new environment can now be imported directly, and side-effects from the old virtualenv are purged.

-------------------------------------------------------------------------------

####Python Macros
Blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah

-------------------------------------------------------------------------------

<a name="smash-for-shell-stuff"/>
SMASH FOR SHELL STUFF
=====================

####CD-hooks
Blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah

-------------------------------------------------------------------------------

####Do What I Mean
Blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah

-------------------------------------------------------------------------------

<a name="smash-for-project-automation"/> <a name="pm"/>
SMASH FOR PROJECT AUTOMATION
============================
Projects are natural abstractions for lots of kinds of work, and will be particularly familiar to anyone who has used an IDE.  In SmaSh, projects are defined by a nickname and associated with a directory.  A project can function as a bookmarks that can be jumped to, and can have a set of command aliases and macros which other projects do not share.  Projects also have *types*, which can either be specified or autodetected based on the contents of the project directory.

**Project Types** are simply lists of strings, such as ["python"], or ["python", "puppet"].  The type of a project may be provided by the user or autodetected by smash.  New user-defined types are encouraged, but they won't have default operations (see below).

**Project Operations** are things you can do to projects, where the builtin operations are *add*, *activate*, *build*, *check*, *test*, and *deactivate*.  The meaning of an operation varies based on project-type, for instance testing a python project will be different than testing a ruby project.  User defined operations are also possible.  Each operation can be specified per project as a list, where the list contains a sequence of shell commands or python callables.  If a given operation is not defined for a given project, a reasonable default for that operation should be guessed based on the project type.  For each operation, here are some examples of the type of actions you might like to perform:

* *Add*: register new project nickname & directory with the Project Manager
* *Activate*: pull fresh code, start project-specific database services or system daemons.
* *Build*: maybe tox for a python project, ant for java or whatever
* *Check*: verify symlinks, start linters or other static analysis
* *Test*: set environment variables and then run unittests
* *Deactivate*: push finished code, stop project-specific database services or other system daemons.

In the sections below, you will find instructions on how to invoke operations and what the default operations will involve for each project type.

-------------------------------------------------------------------------------

**Adding Projects** can be accomplished temporarily with `add_project nickname dir`, or new projects can be permanently added in `~/.smash/config.py`.  If you have a single directory like *~/code* that contains multiple projects, you can turn each subdirectory into a project by setting `project_search_dir` in the smash config file.

-------------------------------------------------------------------------------

**Activating Projects** is done with a command like `proj.nickname`.  (Note: you can use tab-completion over project names).
* Vagrant projects:
    * run "vagrant up"
* Python projects:
    * jump to the project base directory
    * if the project contains one or more virtualenvs, the most recent will be activated

-------------------------------------------------------------------------------

**Deactivating Projects** usually isn't necessary because activating a new project will automatically deactivate the previous project.  To manually deactivate the current project, type `proj._deactivate`[#](#TODO),
* Vagrant projects:
    * run "vagrant halt"
* Python projects:
    * deactivate any virtual environments associated with project ([see also](#))

-------------------------------------------------------------------------------

**Building Projects** is done for the current project using `proj._build`, or for an arbitrary project using `build_project nickname`.
* Python projects:
    * if tox.ini is present
        * runs `tox $TOX_BUILD_ARGS` *(set this in the activation rules)*
    * if setup.py is present run "setup.py develop"
* Doc projects:
    * if there is a README markdown file, generate github style html

-------------------------------------------------------------------------------

**Checking Projects** is done on the current project using `proj._check`, or on an arbitrary project using `check_project nickname`.
* Python projects:
    * run flake8 but ignore any venvs

-------------------------------------------------------------------------------

**Testing Projects** is done for the current project using `proj._test`, or on an arbitrary project `test_project nickname`.  It's difficult to guess in general how project tests should be run, but smash can detect or guess a few different patterns:
* Python projects:
    * try using tox first if tox.ini found
        * runs `tox $TOX_TEST_ARGS` *(set this in the activation rules)*
    * if tox is not found, look for `tests/` or `*/tests` folder,
        * if found, collect and attempt to run with pytest

-------------------------------------------------------------------------------


<a name="dev-installation"/>
DEV INSTALLATION
================

There are two parts to SmaSh: smashlib and the smash shell.  The instructions in the [quickstart section](#quickstart) install *both*.  Installing the shell is atypical for the reasons mentioned in that section, but **if you only want to develop against smashlib**, installation is more typical:

```shell
  $ git clone https://github.com/mattvonrocketstein/smashlib.git
  $ cd smashlib
  $ python setup.py develop
  $ pip install -r requirements.txt
```
