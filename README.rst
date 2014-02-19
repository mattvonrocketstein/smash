
===========
About SmaSh
===========

SmaSh is the smart-shell.  It offers features for project management, a flexible plugin
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

"Do what I mean" is a pretty reasonable expectation for a modern computer program..
that's why we get what we expect when we type "1024*231" into google, namely a numerical
result instead of just a bunch of matching webpages.

Type */etc/* into your shell and what do you see?  Probably something like this:::

   bash:/etc/: Is a directory

No kidding.  I even put a "/" at the end, so probably I know it is a directory and, in the
absence of any other context, I probably want to move into that directory.  Or, if I were
to type out the name of a non-executable file that ends in .txt, chances are good I want to
EDIT THE FILE and not see some kind of error about how the file is not executable.

How would you even go about fixing something like this in bash, where the interface comes
burdened with so many assumptions?

On top of those problems, shells are not at all ideal for software development.  And based
on that point, maybe you're already thinking *"Use emacs/vim/eclipse!"*.  But, I also
personally think that a huge, do-everything IDE is not the True Way.

Still the problems most people solve on a daily basis are similar to the problems from
yesterday, and shell experiences are often characterized by too much repetition.  We fumble with
awkward histories with our control-r's and we do things like build one-off aliases or
scripts and throw them in a *.bashrc* or *~/bin* and there they rot, usually because they
weren't readable a week after they were written, and they weren't quite general enough
to be used everywhere.  Enough is enough!

====================================
IPython+pysh is not quite a solution
====================================

IPython is pretty great, but in many ways is more a framework than a solution.
Even though it does basic shell stuff, out of the box it is primarily intended
for python developers, and not fit for use as a generic shell.  Here are just
a few reasons vanilla IPython and pysh+IPython is not usable as a system
shell:

  - obviously not completely bash-like (nor should it be): 'cd <dir>' works but 'tail -f <file>' does not
  - configuration is too confusing: profiles vs. rc-files vs programmatic api

Although IPython is flexible enough to do almost anything in terms of whatever
triggers, aliases, macros, input pre/post-processing.. adding fancy stuff on to
the IPython core to leverage this functionality (e.g. via profiles) is *still*
not maintainable.


=================
Vision of a Shell
=================

Why do you occasionally go to google to type in things like "1024 * 768" or
"cos(53)" or "current time in zimbabwe"?  And again, why can't it be obvious
that typing "/etc/" by itself clearly means "cd /etc/"/?  My guess is your
shell is just not smart enough, and teaching it to be smart is not so much
difficult as it is simply disorganized.  It takes effort and in the end it
doesn't come out quite the way you hoped.  And that's just for the average
user..

For developers, what is often needed is an environment that functions
simultaneously as a shell and a sort of sketchbook for programming.  The
**pysh** profile for IPython already functions as a sort of Python / Bash
chimera, and SmaSh leverages everything it offers:

  - Simple: all the simplicity of bash when you want it
  - Flexible: all the power of a RealProgrammingLanguage(tm) when you need it
  - Unsurprising: bashy commands and pythony code both work the way you would expect
  - Hybrid: Mixing python and shell code is possible

SmaSh is also extensible, and actually has very little core functionality.
A big part of what it offers is just an organized approach to configuration
management and plugins.  In fact, almost all of what it does happens through
plugins!  Apart from what the bash/python hybrid features that come from pysh,
SmaSh also inherits all the flexibility of IPython in terms of I/O hooks and
pre/post processing.  So go nuts with your domain specific language or ruby's
pry shell or go attach a lisp/lua/node runtime onto this frankenstein
bananaphone piano, see if I care.

================
SmaSh Philosophy
================

SmaSh is installed and modified on a per-user basis; nothing is installed at
the system level.  This is important because, as you continue to add plugins to
smash, any third-party support libraries that are required won't clutter up the
rest of your system.  In particular,

   - Installation, including IPython, is completely inside a python venv at *~/.smash*
   - All configuration is JSON, stored in *~/.smash/etc*
   - All plugins are in *~/.smash/plugins*
   - Core support libraries live in *~/.smash/smashlib*

==========
SmaSh Core
==========


The Project-management Abstraction:
-----------------------------------

**Projects** are typically objects that correspond to directories.
Project names should be kept unique.::

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

Editor and editor preferences
-----------------------------
The editor is invoked by the "ed" magic command.  Editing a file will trigger the
"edit" signal on the SmaSh bus, in case plugins want to trigger on the event.
Arguments to "ed" may be python objects, or files.

    - editor preferences are defined in *~/.smash/etc/editor.json*
    - you can specify one editor for console, and one for windowing environment


Prompt and Aliases:
-------------------

::

  - Alias configuration is stored with JSON
  - Aliases can be global, or stored per project
  - Project-specific aliases do not add clutter when a project is not activated
  - Prompt is split into "components" that can be easily added/substracted on the fly, and
  - Prompts can also be project-specific.

The Plugin Architecture:
-------------------------

Lots of plugins are included with SmaSh (read more below).  I don't necessarily
claim all these are useful to you, and they won't be enabled by default.  The
provided plugins are intended to provide a wealth of examples for some of the
basic things you might want to do.  SmaSh plugins can alter all sorts of things
about the environment that they run in.  For example::

  - loading other plugins
  - altering prompt behaviour
  - altering completion strategies
  - contributing methods, macros, or magic to the shell's global namespace
  - and even alter/act-on command line arguments that SmaSh itself will use.

Plugins can be enabled unconditionally, in which case they are loaded when
SmaSh bootstraps, or they can be loaded conditionally, in which case they are
triggered by project activation or loaded dynamically by another plugin.

To write a plugin you must extend ``smashlib.smash_plugin.SmashPlugin``, and
define an install() method.  From the command line you can use
**smash --install** to "acquire" plugins and move them to **~/.smash/plugins**.
Plugins can be grabbed from disk, or from URLs but the preferred method for
distributing plugins is via github gist's using **smash --install gist://<id>**.

SmaSh tries to encourage writing small plugins without dependencies, but if you
need to reuse code from another plugin, every plugin that's enabled can be imported
at any time from the ``smashlib.active_plugins`` module.  If you require a python
module that may not be installed at the system level, make sure your plugin
specifies values in ``Plugin.requires_modules``.

SmaSh plugins can specify any prerequisites they might have in terms of python
modules, system binaries, or other SmaSh plugins.  At bootstrap, most systems
that involve prerequisites use "priorities" for loading dependencies, but
*SmaSh is different and drama free*.  You specify your prerequisites, and if
your configuration is feasible then SmaSh will determine a consistent ordering
for the bootstrap (or tell you if there is a contradiction).


=========================
Generic Plugins for SmaSh
=========================

Misc environment completion(via smash_env_completer.py)::

  - Bash-compatability: typing "echo $US<tab> completes to $USER, etc

Do what I mean (via smash_dwim.py)::

  - typing "/etc/" means "cd /etc/"
    - actually, this uses pushd so you can popd back to where you came from
  - typing "/etc/hosts" means "edit /etc/hosts"
    - only works whenever /etc/hosts is not executable
    - only works whenever /etc/hosts is small(ish)
    - shows a warning if you will not be able to save the file
    - Wondering which editor will be used?  see editor preferences section.

Hostname completion (via host_completer.py)::

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

Git VCS Integration (via smash_git.py)::

  - If applicable, default prompt includes current branch name
  - Tab completion including:
     - Branch completion in all the right spots
     - File-system completion when using 'git mv' or 'git add'
     - smart branch/file-system completion when using 'git diff'
  - Various default aliases and places to put more (making ".git/config" optional)
  - Should you be inclined: hopefully enough abstraction here to easily support other VCS's

Notification support (experimental)::

  - Asynchronous notifications via freedesktop
  - When this works, it's pretty great, but..
     - currently no support for osx (growl)
     - this may involve extra system-level requirements
     - may require some fiddling to get it to work outside of ubuntu/gnome (!)

=================================
Python Specific Plugins for SmaSh
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
  4) if name matches a file, determine file type with file(1)
  5) if name matches a host, show the IP address according to host files
  6) if name matches an internet domain, show the IP address according to DNS


==============================
Installation and Prerequisites
==============================

SmaSh works well with python 2.6, and 2.7 and possibly earlier.  SmaSh is compatible
with python3 only insofar as IPython is.  You will need virtualenv installed at the
system level ( in debian-based distros, use **apt-get install python-virtualenv**),
but anything else that is required should be installed automatically by the
following steps.

  To install, clone this repository::

    $ mkdir ~/code; cd ~/code
    $ git clone git://github.com/mattvonrocketstein/smash.git

  Install it (development mode obligatory for now, since SmaSh is beta)::

    $ python setup.py develop

  If everything went well, you should be able to run 'smash' now::

    $ smash

====================
Working with Plugins
====================

By default, enabled plugins are kept to a minimum.  You can get a list of available,
enabled, and disabled plugins like this::

    $ smash --list

If you use git VCS, I suggest enabling support for that.  This will customize your prompt
to show the current branch, turn on various completers, add convenient aliases.::

    $ smash --enable git_completers.py
      bootstrap: launching with rc-file: /home/testing/.smash/etc/smash.rc
      git_completer: setting prompt to use git vcs
      project_manager: loading config: /home/testing/.smash/etc/projects.json
      plugin_manager: enabling git_completers.py

Changes will take affect when you next relaunch the shell.

If you're a python programmer, I suggest turning on a few more:::

    $ smash --enable venv_prompt.py
    $ smash --enable pip_completer.py
    $ smash --enable setup_completer.py
    $ smash --enable which.py
    $ smash --enable fabric_support.py

From inside SmaSh, you can interact with the plugins via the **plugins** command.
(This command is actually an object that represents the plugin manager.  If you
want the plugin objects themselves use **plugins.plugins**.  If you want the
namespace defined by a given plugin file, import
**smashlib.active_plugins.some_plugin_name**)::

    [~]> plugins?

    Smash-plugin information:
      config-file: /home/matt/.smash/etc/plugins.json

    |                       name | enabled | errors |
    -------------------------------------------------
    |          apt_completers.py |    True |      0 |
    |     currency_conversion.py |    True |      0 |
    |              djangoisms.py |   False |      0 |
    |          fabric_support.py |   False |      0 |
    |          git_completers.py |    True |      0 |

=====================
Working with Projects
=====================

First open *~/.smash/etc/projects.json* in the editor of your choice.

The simplest thing you can do is add a single directory as a project.  To do that,
add a line like this to the "instructions" section:::

   ["bind",     ["~/myproject"], {}]

To add all directories under a certain directory, add an entry like this:::

   ["bind_all", ["~/code"],          {}],

Note that **bind_all** is not recursive, it only goes one layer deep.
Once you've added this and restarted SmaSh, then it knows about your projects:::

   matt@vagabond:~$ smash
     bootstrap: launching with rc-file: /home/matt/.smash/etc/smash.rc
     project_manager: loading config: /home/matt/.smash/etc/projects.json
     project_manager: binding /home/matt/code (21 projects found)
   [~]>

The shell's handle for interacting with projects is simply "proj".  It already
exists there, and you can query it for some simple information like this:::

   [~]> proj?

   Found Projects:
   |                 name |                        path | virtualenv |           vcs |
   -----------------------------------------------------------------------------------
   |           robotninja |           ~/code/robotninja |     ./node | GitRepository |
   | readertray-read-only | ~/code/readertray-read-only |        N/A |    Subversion |
   |          plurlpicker |          ~/code/plurlpicker |        N/A |           N/A |


Your projects might be registered, but they have not yet declared any post or
pre-invocation hooks.  Still, you immediately get a simple alias for changing
directories.  (From this point on, debugging-messages are turned on so that the
reader can get a better idea of what's happening.) Since I have a project called
robotninja in my ~/code directory, I can do this ::

   [~]> proj.robotninja
     pre_invoke{'name': u'robotninja'}
   [~/code/robotninja]>

Useful, but that was kind of boring.  Let's add an alias that means different things
depending on which project you've activated.  You can see from the table above that
one project is using subversion for VCS, whereas another is using git.. so how about
we make one "status" alias that does the right thing in the right place?  Open
*~/.smash/etc/projects.json* again, and make your alias section look something like
this:::

  'aliases': {
    'robotninja': ['status git status',],
    'readertray-read-only':['status svn status']
   }

The first time when only "proj.robotninja" was used, the project was "invoked", not
"activated".  Activation is accomplished like so:::

   [~]> proj.robotninja.activate
     pre_invoke{'name': u'robotninja'}
     pre_activate: {'name': u'robotninja'}
     post_activate: {'name': u'robotninja'}
     alias_manager: adding new aliases for "robotninja"
     alias_manager:  added 1 aliases for this project
     project_manager: resetting CURRENT_PROJECT

Note that project "activation" implies "invocation" in the debugging information
printed above.  Via *invocation* we changed directories and via *activation* we
gained an alias.::

   [~/code/robotninja]> status
     # On branch voltron
     # Untracked files:
     #   (use "git add <file>...

So that 'status' alias works as expected.  Let's try the other one..::

   [~/code/robotninja]> proj.readertray_read_only.activate
     pre_invoke: {'name': u'readertray-read-only'}
     pre_deactivate: {'name': u'robotninja'}
     post_deactivate: {'name': u'robotninja'}
     pre_activate: {'name': u'readertray-read-only'}
     alias_manager: killing old aliases for "robotninja"
     alias_manager: removed 1 aliases from the previous project
     post_activate: {'name': u'readertray-read-only'}
     alias_manager: adding new aliases for "readertray-read-only"
     alias_manager:  added 1 aliases for this project
     project_manager: resetting CURRENT_PROJECT

   [~/code/readertray-read-only]> status
     M       readergui.py

Neato, so shows that the 'status' alias is now attached to subversion rather than git.

======================
Working with Bookmarks
======================

Bookmarks are very similar to aliases. blah, blah blah

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
