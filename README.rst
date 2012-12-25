=====
About
=====

Smash is the smart-shell, a python/bash hybrid which builds on the pysh profile for IPython.  It
offers features for project management, virtual environment support, a flexible plugin
architecture that is easy to use, and simple JSON configuration files that try to be as
sane as possible.


===========
The Problem
===========

Shells are still annoying!

  - No one wants to manage zillions of aliases or arcane readline configurations
  - Things like sed / awk are great for quick hacks, but are obscure and not maintainable.
  - Shells are not conveniently modular, and do not perform well for things like
     - multiple projects
     - multiple use-cases
     - domain specific languages
  - Minimal or awkward context-awareness (things like pre/post "dir-change" triggers)
  - Not ideal for software development in many ways

Based on the last point, maybe you're already thinking "`Use emacs/vim/eclipse!`", but, I also
personally think that a huge, do-everything IDE is not the True Way.  The problems most people solve
on a daily are similar to the problems from yesterday, and shell experiences are often characterized
by too much repetition.  We fumble with awkward histories with our control-r's and we do things like
build one-off aliases or scripts and throw them in a .bashrc or ~/bin and they rot, usually because
they weren't quite general enough to use everywhere.

====================================
pysh+IPython is not quite a solution
====================================

IPython is fairly great, but in many ways is more a framework than a solution, and even though it does
basic shell stuff, out of the box it is primarily intended for python developers, and not fit for use
as a generic shell.  Here are just a few reasons vanilla IPython and pysh+IPython are not usable as
system shells:

  - obviously not completely bash-like (nor should it be): 'cd <dir>' works but 'tail -f <file>' does not
  - lack of consistency: profiles vs. rc-files vs straight programmatic api configuration is confusing

Although IPython is flexible enough to do almost anything in terms of triggers, aliases, macros,
input pre/post-processing.. adding fancy stuff on to the IPython core to leverage this
functionality (e.g. via profiles) is *still* not maintainable.



======================
SmaSh is a Way Forward
======================

What is needed is an environment that functions simultaneously as a shell and a
sort of sketchbook for programming.  The ``pysh`` profile for IPython already
functions as a sort of Python / Bash chimera, and SmaSh leverages everything it
offers:

  - Simple: all the simplicity of bash when you want it
  - Flexible: all the power of a RealProgrammingLanguage(tm) when you need it
  - Unsurprising: bashy commands and pythony code both work the way you would expect
  - Hybrid: Mixing python and shell code is possible

SmaSh is extensible and although it is built on top of pysh, and actually has very
little core functionality.  A big part of what it offers  is an organized approach
to configuration management and plugins.  In fact, almost all of what it does happens
through plugins.  Apart from what the bash/python hybrid features that come from pysh,
SmaSh also inherits all the flexibility of IPython in terms of I/O hooks and pre/post
processing.  So go nuts with your domain specific language or ruby's pry shell or go
attach a lisp-lua-node runtime onto this frankenstein bananaphone piano, see if I care.

================
Smash Philosophy
================
Smash is installed and modified on a per-user basis; nothing is installed at the system level.
This is important because as you continue to add plugins to smash, any third-party support
libraries that are required won't clutter up the rest of your system.

   - Installation, including IPython, is completely inside a python virtual-env located at ~/.smash
   - All configuration is JSON, stored in ~/.smash/etc
   - All plugins are in ~/.smash/plugins
   - Core support libraries live in ~/.smash/smashlib


==========
Smash Core
==========


The Plugin Architecture:
-------------------------

Plugins can be enabled unconditionally, in which case they are loaded when SmaSh bootstraps,
or they can be loaded conditionally, in which case they are triggered by project activation
or loaded dynamically by another plugin.

To write a plugin you must extend smashlib.smash_plugin.SmashPlugin, and define an install()
method.  From the command line you can use `smash --install` to "acquire" plugins and move them
to ~/.smash/plugins.  Plugins can be grabbed from disk, or from url's but the preferred method
for distributing them is via github gist's using `smash --install gist://<id>`.

SmaSh plugins can do all sorts of things to the shell by
  - loading other plugins
  - altering prompt behaviour
  - altering completion strategies
  - contributing methods, macros, or magic to the shell's global namespace


The Project-management Abstraction:
-----------------------------------

`Projects` are typically objects that correspond to directories.

  - Bind individual directories (`~/myproject`) or directories of directories (`~/code/*`)
  - Project configuration is stored with JSON in `~/.smash/etc/projects.json`
     - you can manipulate it via the command-line or edit config-files yourself
  - Projects can be "activated", "invoked", or "deactivated" and each can trigger pre/post actions
  - Pre/post actions might mean convenient side-effects such as
     - activating a virtual environment
     - starting a virtual machine
     - opening a web page
     - whatever else you want..
  - Projects can have alias groups
     - alias groups are activated when the project is
     - alias groups are deactivated when you leave the project
  - Projects can be watched for changes, triggers for linters can be added, etc
  - Project code can be searched asynchronously, results delivered in a way that doesnt clutter your screen
  - Project code does not necessarily need to be python, but if it is you get sweet benefits

Prompt and Aliases:
-------------------
  - Alias configuration is stored with JSON
  - Aliases can be global, or stored per project
  - Aliases that are project specific do not clutter things up when a project is not activated
  - Prompt is split into "components" that can be easily added/substracted on the fly, and
  - Prompts can also be project-specific.

=========================
Generic Plugins for Smash
=========================

Hostname completion:
---------------------
  - works for ssh
  - works for any program using standard uri's like ftp://, http://, etc

Browser Integration:
--------------------
  - manage and open bookmarks globally or per-project
  - performs web searches with http://duckduckgo.com API, allowing for:
    - direct search of stack-overflow, django docs, pypi, etc
    - asynchronous notification that doesnt clutter your display (via growl-style popups)
  - reddit plugin

Git VCS Integration:
--------------------
  - If applicable, default prompt includes current branch name
  - Tab completion including:
    - Branch completion in all the right spots
    - File-system completion when using 'git mv' or 'git add'
    - smart branch/file-system completion when using 'git diff'
  - Various default aliases and places to put more (making .git/config optional)
  - Should you be inclined: hopefully enough abstraction here to easily support other VCS's



=================================
Python Specific Plugins for Smash
=================================

Misc extra completers

   - Completers for accessing python dictionaries
   - Completers for setup.py
   - Pip completers
      - tab-completion over the standard pip subcommands
      - tab-completion over contents of requirements.txt if it's in the working directory


Virtual-Environments:

  - venvs can be activated/deactivated cleanly, and without lasting side-effects
  - ``Project activation`` can trigger venv-activation

Fabric integration:

  - tab-completion over fabfile commands
  - programmatic access to the functions themselves
  - PS: this plugin is a good example of a minimal "post-dir-change" trigger

Unit tests:

  - post-dir-change hook finds `tests/` or `tests.py` in working directory
  - or, scan everything under this working-directory or a known Project
  - attempts to detect what type of unittests these are via static analysis (django/vanilla unittest/etc)
  - test files are enumerated and shortcuts for running them quickly are updated


Enhanced 'which'

  1) for unix shell commands, ``which`` works as usual
  2) failing (1), if the name matches a python objects in the global namespace, show the file that defined it
  3) failing (3), if the name matches an importable module, show the path it would be imported from



======================
Possible deal-breakers
======================

SmaSh unfortunately will need IPython==0.10 installed in it's sandbox in ~/.smash, because
later versions of IPython are not compatible ``pysh`` IPython profile, and I have not gotten
around to porting it yet.

One current limitation of the combination of pysh / IPython / SmaSh is a lack of job control
in the sense that you might be used to.  Specifically you can background tasks with an ``&``
as usual, but ``fg`` does not resume.  At first this seemed horrible but in practice I think
this consideration is not very important- shells are cheap to spawn and a workflow around
``screen`` works better anyway.

Currently, SmaSh plugins must be written in python.  However, a very simple python plugin,
say for bash or ruby support, should be able to "build a bridge" between that language and
SmaSh.  If you're interested in helping with this, send me a message about your use-case
and I would be happy to help.

=============
Related Links
=============

  - ``ipython`` http://ipython.org/ipython-doc/dev/interactive/shell.html
  - ``pysh`` http://faculty.washington.edu/rjl/clawpack-4.x/python/ipythondir/ipythonrc-pysh



============
Other Shells
============

  - ``xiki`` (a wiki inspired gui shell) http://xiki.org/
