title: Smash
menu-position: 0
---

[quickstart](#quickstart) | [overview](#overview)



##ABOUT

Smash is a smart shell.  It offers features for project management, a flexible plugin architecture that is easy to use, and simple configuration files that try to be as sane as possible.  [Python developers](#smash-for-python-devs) will be particularly interested because it also happens to host a full-fledged python runtime via IPython, but non-python developers can safely ignore that feature.  Smash leverages existing system [tab completion](#tab-completion) setup, apart from variable/keyword completion in python namespaces.  Smash builds on, and offers very sophisticated support for python virtual environments.

<a id="quickstart"></a>
##QUICKSTART

The smash installation happens in a sandbox, does not require root, and will not interefere with existing versions of IPython.  The cost of this is that setup is a little bit nonstandard and `setup.py` should not be used directly unless you only want to develop against the support libraries (for that see: [dev installation](#dev-installation))



```shell
  $ sudo apt-get install git-core python-virtualenv python-dev
  $ bootstrap=https://raw.githubusercontent.com/mattvonrocketstein/smash/master/bootstrap.sh
  $ curl $bootstrap | bash
  $ ~/bin/smash
```

<a id="philosophy"></a>
##BUT.. WHY??

So, *why build yet another shell?*  Put simply, shells still kind of suck.  The main problem is that classic shells are inflexible and not easy to extend.  If you do manage to extend them, you probably had to do it with shell code, and so the result is something that's fragile and difficult to maintain.  Just for the sake of an example, let's consider the problem of a "do what I mean" extension for your shell, where if you type something that looks like a url then the url is opened automatically for you.  To effect a pre-exec style hook in bash, you'll have to do [black magic](http://www.twistedmatrix.com/users/glyph/preexec.bash.txt) with the `DEBUG` trap (ugh).  Zsh is better, but of course you'll still be writing (or at least invoking) your hooks in shell code.  This works at first, but things start to get messy when issues of code-reuse come up, or if you want to [invoke hooks conditionally](#pm), etc.  If you still think the do-what-i-mean puzzle sounds easy to solve in your shell, consider the problem of colorizing random structured data (maybe json or server logs) sent to stdout!

SmaSh's close integration with python itself is a huge plus, but it's also just a side effect of fixing the main problems around making a shell that is truly flexible and nontrivially extensible.

<a id="overview"></a>
##FEATURE OVERVIEW

####Standard System Shell + Python Support
SmaSh functions seamlessly as a normal system shell, but it also a full fledged python interpretter.  It does shell stuff in the shell places, and python stuff in the python places.

![screenshot1](/docs/screenshots/demo-python-bash.png?raw=true "screenshot1")

If you're a bash user or an ipython user, your existing configuration efforts can also be [inherited automatically](#TODO-config-inheritance).  If you don't care anything about python, you can ignore that aspect of the shell completely.  If you *are* a python programmer, you probably spend as much time in a python interpretter as you do in shell.  You can trade those two windows for one to reduce screen clutter, as well as enjoy all the [other python friendly features of smash](#smash-for-python-devs).

-------------------------------------------------------------------------------

<a id="prompts"></a>
####Prompt
By default smash ships with the wonderfully dynamic [liquidprompt tool](#https://github.com/nojhan/liquidprompt).  Liquidprompt has rich options for configuration and it's recommended that you [configure it in the normal way](https://github.com/nojhan/liquidprompt#features-configuration), but, some of these options can be overridden from `~/.smash/config.py`.  The default liquidprompt configuration features a prompt that shows activated python virtual environments, as well as VCS branch and commit/stash status, etc.  Other options include everything from cpu/battery status to write-permissions for the current directory.  Take a look at how it updates below based on the context:

![screenshot1](/docs/screenshots/demo-liquidprompt.png?raw=true "screenshot1")

-------------------------------------------------------------------------------

<a id="tab-completion"></a>
####Tab-completion system
Depending on the context, tab completion information is derived either from ipython (for python namespaces, ipython aliases, etc) or directly from bash (for system commands / paths, hostnames, VCS subcommands, debian packages, whatever your system supports).  Thus if you now use bash exclusively<sup>**</sup> then this means that no effort at all goes into porting old completers into smash shell.  For building new completion mechanisms, you have the option of writing them inside or outside of smash, based on your preference.

![screenshot1](/docs/screenshots/demo-completion.png?raw=true "screenshot3")

<sub>**: if you are a zsh wizard, please help fix [issue 11](https://github.com/mattvonrocketstein/smash/issues/11)!</sub>

-------------------------------------------------------------------------------

<a id="configuration"></a>
####Configuration
Lorem Ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum

-------------------------------------------------------------------------------

<a id="plugins"></a>
####Plugins / Extensions

Smash has lots of plugins that extend or modify the core behaviour.  Some plugins are turned on by default, some are complete but opt-in, and some are works in progress, demonstrations, or proof-of-concepts.  The smash core tries to be small and just includes the essential stuff, so it's safe to assume that most of the functionality described on this page is effected by plugins.

**Writing new plugins** is fairly easy, but may not be necessary for your application (see the [configuration section](#configuration)). If you do need to write a plugin, read on, but first a bit of background.  Smash is built on top of [IPython](http://ipython.org/) and is in fact itself an IPython extension.  *Smash plugins are essentially ipython extensions which require smash*, but it can be useful to differentiate the terminology.  Before going much further it's probably a good idea to check out the existing IPython docs on [writing extensions](http://ipython.org/ipython-doc/dev/config/extensions/).

If you want to do simple stuff like just writing new commands then a tutorials for [writing IPython magic](#http://catherinedevlin.blogspot.com/2013/07/ipython-helloworld-magic.html) will probably be all you need.

If you want to get your hooks into smash-specific events like "directory change" or "virtual environment deactived" then read [this documentation](#TODO) about the smash event system. For an example of writing new tab-completion stuff, check out [the code for the fabric completer](#TODO).  For an example of input preprocessing see the [currency converter code](#TODO).  Foran example of all-else-fails input processing (meaning input was neither bash nor python) see [the do-what-I-mean code](#TODO).

-------------------------------------------------------------------------------

<a id="smash-for-python-devs"></a>
SMASH FOR PYTHON DEVS
=====================

####Python Virtualenv Support
SmaSh has sophisticated virtualenv support which is useful particularly if you're working on multiple projects or working with multiple major versions of the same software.  Activating/deactivating venvs is done with `venv_activate some_dir` and `venv_deactivate`, respectively.  This not only updates your $PATH, but updates the python runtime.  Modules from the new environment can now be imported directly, and side-effects from the old virtualenv are purged.

-------------------------------------------------------------------------------

####Python Macros
Lorem Ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum

-------------------------------------------------------------------------------

<a id="smash-for-shell-stuff"></a>
SMASH FOR SHELL STUFF
=====================


####CD-hooks
Lorem Ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum

-------------------------------------------------------------------------------

<a id="dwim"></a>
####Do What I Mean
Lorem Ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum

-------------------------------------------------------------------------------

####Shell-related Problems
Most shell stuff "just works", even when it looks like the grammar for shell vs. python might be ambiguous (for instance, try: `[ string ] && echo its true || echo its false`).  In the event of name collisions, the python namespace typically has preference over the system commands, but this is easy to fix by just deleting the python shadow:

```shell
   smash$ ls
   file1     file2     file3     file4
   file5     file6     file7     file8
   smash$ ls="python namespace shadow"
   smash$ ls
   Out[3]: "python namespace shadow"
   smash$ del ls
   smash$ ls
   file1     file2     file3     file4
   file5     file6     file7     file8
```



If things aren't "just working", then file an issue or maybe try **IPython's various built-ins**.  The `%%bash` magic might be useful for pasting lots of lines.  The desperate or the paranoid can always prefix commands like `! ls` to ensure they go straight to shell and are not interpretted as python.    Out of the box IPython even supports some limited [mixed python/bash programming](#).


-------------------------------------------------------------------------------

<a id="smash-for-project-automation"></a> <a id="pm"></a>
SMASH FOR PROJECT AUTOMATION
============================
Projects are natural abstractions for lots of kinds of work, and will be familiar to anyone who has used an IDE.  In smash, project management features are essentially a plugin or extension, and because the "project" concept is flexible and powerful for all sorts of automation this is a pretty big topic.  Working with projects is [described in detail here](#), and what follows is just a summary.

*A project is defined by a nickname and associated with a directory.*  In the simplest case a project can function as merely a bookmark that can be jumped to, or for more involved projects you might want a set of command aliases and macros which other projects do not share.  Projects also have *types* and *operations*, which can either be specified or autodetected based on the contents of the project directory.  The default operations and some examples of what they might involve for your project are described below:

For each operation, here are some examples of the type of actions you might like to perform:

* *Add*: register new project nickname & directory with the Project Manager
* *Activate*: pull fresh code, start project-specific database services or system daemons.
* *Build*: maybe tox for a python project, ant for java or whatever
* *Check*: verify symlinks, start linters or other static analysis
* *Test*: set environment variables and then run unittests
* *Deactivate*: push finished code, stop project-specific database services or other system daemons.



<a id="dev-installation"></a>
DEV INSTALLATION
================

There are two parts to SmaSh: smashlib and the smash shell.  The instructions in the [quickstart section](#quickstart) install *both*.  Installing the shell is atypical for the reasons mentioned in that section, but **if you only want to develop against smashlib**, installation is more typical:

```shell
  $ git clone https://github.com/mattvonrocketstein/smashlib.git
  $ cd smashlib
  $ python setup.py develop
  $ pip install -r requirements.txt
```
