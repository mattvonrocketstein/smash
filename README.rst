
===========
About SmaSh
===========

Smash is the smart-shell.  It offers features for project management, a flexible plugin
architecture that is easy to use, and simple JSON configuration files that try to be as
sane as possible.  Python developers might be particularly interested because it also
happens to be a python/bash hybrid which builds on the pysh profile for IPython.  It builds
on, and offers very sophisticated support for python virtual environments.


===========
The Problem
===========

Shells are still annoying!::

  - No one wants to manage zillions of aliases or arcane readline configurations.
  - Things like sed / awk are great for quick hacks, but are obscure and not maintainable.
  - Shells are not conveniently modular, and do not perform well for things like:
    - multiple projects,
    - multiple use-cases,
    - or domain specific languages.
  - Shells offer only minimal or awkward context-awareness
    - no triggers for things like pre/post "dir-change"
    - no hooks for pre/post processing of IO

Shells are also not ideal for software development.  And based on that point, maybe
you're already thinking *"Use emacs/vim/eclipse!"*.  But, I also personally think that
a huge, do-everything IDE is not the True Way.

Still the problems most people solve on a daily are similar to the problems from yesterday,
and shell experiences are often characterized by too much repetition.  We fumble with
awkward histories with our control-r's and we do things like build one-off aliases or
scripts and throw them in a *.bashrc* or *~/bin* and there they rot, usually because they
weren't readable a week after they were written, and they weren't quite general enough
to be used everywhere.

====================================
IPython+pysh is not quite a solution
====================================

IPython is pretty great, but in many ways is more a framework than a solution.  Even though it does
basic shell stuff, out of the box it is primarily intended for python developers, and not fit for use
as a generic shell.  Here are just a few reasons vanilla IPython and pysh+IPython are not usable as
system shells::

  - obviously not completely bash-like (nor should it be): 'cd <dir>' works but 'tail -f <file>' does not
  - lack of consistency: profiles vs. rc-files vs straight programmatic api configuration is confusing

Although IPython is flexible enough to do almost anything in terms of whatever triggers, aliases, macros,
input pre/post-processing.. adding fancy stuff on to the IPython core to leverage this functionality
(e.g. via profiles) is *still* not maintainable.


=================
Vision of a Shell
=================

Why do you occasionally go to google to type in things like "1024 * 768" or "cos(53)" or
"current time in zimbabwe"?  My guess is your shell is just not smart enough, and
teaching it to be smart is not so much difficult as it is simply disorganized.  It
takes effort and in the end it doesn't come out quite the way you hoped.  And that's
just for the average user.  For developers, what is often needed is an environment that
functions simultaneously as a shell and a sort of sketchbook for programming.  The **pysh**
profile for IPython already functions as a sort of Python / Bash chimera, and SmaSh
leverages everything it offers:

  - Simple: all the simplicity of bash when you want it
  - Flexible: all the power of a RealProgrammingLanguage(tm) when you need it
  - Unsurprising: bashy commands and pythony code both work the way you would expect
  - Hybrid: Mixing python and shell code is possible

SmaSh is also extensible, and actually has very little core functionality.  A big part of what it
offers is just an organized approach to configuration management and plugins.  In fact, almost
all of what it does happens through plugins!  Apart from what the bash/python hybrid features
that come from pysh, SmaSh also inherits all the flexibility of IPython in terms of I/O hooks
and pre/post processing.  So go nuts with your domain specific language or ruby's pry shell or
go attach a lisp/lua/node runtime onto this frankenstein bananaphone piano, see if I care.

================
Smash Philosophy
================

Smash is installed and modified on a per-user basis; nothing is installed at the system level.
This is important because, as you continue to add plugins to smash, any third-party support
libraries that are required won't clutter up the rest of your system.  In particular,

   - Installation, including IPython, is completely inside a python virtual-env located at *~/.smash*
   - All configuration is JSON, stored in *~/.smash/etc*
   - All plugins are in *~/.smash/plugins*
   - Core support libraries live in *~/.smash/smashlib*

==========
Smash Core
==========


The Project-management Abstraction:
-----------------------------------

**Projects** are typically objects that correspond to directories.::

  - Bind individual directories ("~/myproject") or directories of directories ("~/code/"")
  - Project configuration is stored with JSON in "~/.smash/etc/projects.json"
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
  - Project code can be searched asynchronously, results shown in a way that doesnt clutter the screen
  - Project code does not necessarily need to be python, but if it is you get sweet benefits

Prompt and Aliases:
-------------------

::

  - Alias configuration is stored with JSON
  - Aliases can be global, or stored per project
  - Aliases that are project specific do not clutter things up when a project is not activated
  - Prompt is split into "components" that can be easily added/substracted on the fly, and
  - Prompts can also be project-specific.

The Plugin Architecture:
-------------------------

Lots of plugins are included with SmaSh (read more below).  I don't necessarily claim all these
are useful to you, and they won't be enabled by default.  The provided plugins are intended to
provide a wealth of examples for some of the basic things you might want to do.  SmaSh plugins
can alter all sorts of things about the environment that they run in.  For example::

  - loading other plugins
  - altering prompt behaviour
  - altering completion strategies
  - contributing methods, macros, or magic to the shell's global namespace
  - and even alter/act-on command line arguments that SmaSh itself will use.

Plugins can be enabled unconditionally, in which case they are loaded when SmaSh bootstraps,
or they can be loaded conditionally, in which case they are triggered by project activation
or loaded dynamically by another plugin.

To write a plugin you must extend ``smashlib.smash_plugin.SmashPlugin``, and define an install()
method.  From the command line you can use **smash --install** to "acquire" plugins and move them
to **~/.smash/plugins**.  Plugins can be grabbed from disk, or from URLs but the preferred method
for distributing plugins is via github gist's using **smash --install gist://<id>**.

SmaSh tries to encourage writing small plugins without dependencies, but if you need to reuse
code from another plugin, every plugin that's enabled can be imported at any time from
the ``smashlib.active_plugins`` module.  If you require a python module that may not be installed
at the system level, make sure your plugin specifies values in ``Plugin.requires_modules``.

SmaSh plugins can specify any prerequisites they might have in terms of python modules, system
binaries, or other SmaSh plugins.  At bootstrap, most systems that involve prerequisites use
"priorities" for loading libraries-- *SmaSh is different and drama free*.  You specify your
prerequisites, and if your configuration is feasible then SmaSh will determine a consistent
ordering for the bootstrap or tell you if there is a contradiction.


=========================
Generic Plugins for Smash
=========================

Hostname completion::

  - works for ssh
  - works for any program using standard URIs like ftp://, http://, etc
  - uses the contents of "~/.smash/etc/hosts.json" and, if available, contents of /etc/hosts

Enhanced Bookmarks::

  - offers sophisticated bookmarks, globally or per-project
  - bookmark directories, URLs, macros
  - bookmark nonstandard URIs like ssh://person@place
  - launching bookmark actions is keyboard-friendly

Browser Integration::

  - manage and open bookmarks, (global or per-project)
  - performs web searches with http://duckduckgo.com API, allowing for:
    - direct search of stack-overflow, django docs, pypi, etc
    - asynchronous notification that doesnt clutter your display (via growl-style popups)

Git VCS Integration::

  - If applicable, default prompt includes current branch name
  - Tab completion including:
     - Branch completion in all the right spots
     - File-system completion when using 'git mv' or 'git add'
     - smart branch/file-system completion when using 'git diff'
  - Various default aliases and places to put more (making ".git/config" optional)
  - Should you be inclined: hopefully enough abstraction here to easily support other VCS's

Notification support::

  - Asynchronous notifications via freedesktop
  - When this works, it's pretty great, but..
     - currently no support for osx (growl)
     - this may involve extra system-level requirements
     - may require some fiddling to get it to work outside of ubuntu/gnome (!)

=================================
Python Specific Plugins for Smash
=================================

Misc extra completers::

   - Completers for accessing python dictionaries
   - Completers for setup.py
   - Pip and easy_install completers
      - Completion over the standard pip subcommands
      - Completion over contents of requirements.txt if it's in the working directory


Virtual-Environments::

  - Venv's can be activated/deactivated cleanly, and without lasting side-effects
  - Close integration with projects such that
     - if a project is activated and it is a venv, it will be activated
     - if a project contains a venv at the top-level, that venv will be activated

Fabric integration::

  - Completion over fabfile commands
  - Programmatic access to the functions themselves
  - PS: this plugin is a good example of a minimal "post-dir-change" trigger

Unit tests::

  - post-dir-change hook finds `tests/` or `tests.py` in working directory
  - or, scan everything under this working-directory or a known Project
  - attempts to detect what type of unittests these are via static analysis (django/vanilla unittest/etc)
  - test files are enumerated and shortcuts for running them quickly are updated
  - etc

Enhanced **which** with cascading search behaviour::

  1) for unix shell commands, "which" works as usual
  2) if the name matches a python obj in the global namespace, show the file that defined it
  3) if the name matches an importable module, show the path it would be imported from
  4) if name matches a host, show the IP address according to host files
  5) if name matches an internet domain, show the IP address according to DNS



==============================
Installation and Prerequisites
==============================

SmaSh works well with python 2.6, and 2.7 and possibly earlier.  SmaSh is comptible
with python3 only insofar as IPython is.  You will need virtualenv installed at the
system level ( in debian-based distros, use **apt-get install python-virtualenv**).

=============
Related Links
=============

  - ``ipython`` http://ipython.org/ipython-doc/dev/interactive/shell.html
  - ``pysh`` http://faculty.washington.edu/rjl/clawpack-4.x/python/ipythondir/i
  - ``virtualenv for python`` http://some-link-here

============
Other Shells
============

  - ``xiki`` (a wiki inspired gui shell) http://xiki.org/
