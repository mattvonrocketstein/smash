=====
About
=====

Smash is the smart-shell, a python/bash hyrbid building on the pysh profile for IPython.

===========
The problem
===========

Shells are still annoying!

  * No one wants to manage zillions of aliases or arcane readline configurations
  * Things like sed / awk are great for quick hacks, but are not maintainable, they get obscure really quick.
  * Not conveniently modular and do not perform well for multiple projects / multiple use-cases
  * Minimal or awkward context-awareness (i.e. things like pre/post "dir-change" triggers)
  * Not ideal for software development in many ways (and neither is a huge do-everything IDE the True Way)

IPython is great but in many ways is more a framework than a solution, and even though
it does basic shell stuff, out of the box it is not fit for normal use.

  * obviously not completely bash-like (nor should it be): 'cd <dir>' works but 'tail -f <file>' does not
  * lack of consistency: profiles vs. rc-files vs straight programmatic api configuration gets confusing

================================
Smash is the best of both worlds
================================

What is needed is an environment that functions simultaneously as a shell and a sort of sketchbook
for programming.  The `pysh` profile for IPython already functions as a sort of Python / Bash chimera:

  * Simple: all the simplicity of bash when you want it
  * Flexible: all the power of a RealProgrammingLanguage(tm) when you need it
  * Unsurprising: bashy commands and pythony code both work the way you would expect
  * Hybrid: Mixing python and shell code is possible

===================
Smash is Extensible
===================

Smash actually has very little core functionality but gets most of what it has through plugins.
Smash inherits all the flexibility of IPython in terms of I/O hooks and pre/post processing so go
nuts with your DSL or go attach a lisp-lua-ruby runtime onto this frankenstein genius, smash will
love it too.

=========================
Generic Plugins for Smash
=========================

Git VCS Integration:
--------------------
  * if applicable, default prompt includes current branch name
  * Tab completion including
    * branch completion when using checkout
    * file-system completion when mv/add
    * smart branch/file-system when using diff
  * various default aliases and places to put more

Abstractions for project-management:
------------------------------------
  * directories can be registered as projects
  * project configuration is manipulated via the command-line and persisted for you with JSON
  * projects can activate their own alias groups that are not shared by the shell at large
  * project code does not necessarily need to be python, but if it is you get sweet benefits
  * projects can be watched for changes, triggers for linters can be added, etc
  * code can be searched asynchronously, results delivered in a way that doesnt clutter your screen
  * projects can be "activated", which might mean convenient side-effects like
    * activating a virtual environment
    * starting a virtual machine
    * opening a web page


=================================
Python Specific Plugins for Smash
=================================

Virtual-Environments:
---------------------
  * venvs can be activated/deactivated cleanly and without lasting side-effects
  * project activation (in the sense of the plugin above) can trigger

Fabric integration:
-------------------
  * tab-completion over fabfile commands
  * programmatic access to the functions themselves
  * additionally, this plugin is a good example of a "post-dir-change" trigger

======================
Possible deal-breakers
======================

At this point you unfortunately will need IPython==0.10 installed, and even more unfortunately
you probably need it installed at the system level.  (Later versions of IPython are not compatible
`pysh` IPython profile, and I have not gotten around to porting it yet).  You will likely need it
installed at the system level because smash itself aims at managing virtual-envs.. running it from
one might be possible but could lead to confusion.

One current limitation of the combination of pysh / ipython / smash is a lack of job control
in the sense that you might be used to.  Specifically you can background tasks with an `&` as
usual, but `fg` does not resume.  At first this seemed horrible but in practice I think this
consideration is not very important because shells are cheap to spawn (and a workflow around
`screen` works better anyway).

=============
Related Links
=============

  * http://ipython.org/ipython-doc/dev/interactive/shell.html

============
Other Shells
============
