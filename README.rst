=====
About
=====

Smash is the smart-shell, a python/bash hybrid which builds on the pysh profile for IPython.  It
offers features for project management, virtual environment support, a plugin architecture, and
simple JSON configuration files that try to be as sane as possible.


===========
The problem
===========

Shells are still annoying!

  * No one wants to manage zillions of aliases or arcane readline configurations
  * Things like sed / awk are great for quick hacks, but are obscure and not maintainable.
  * Shells are not conveniently modular, and do not perform well for multiple projects / use-cases
  * Minimal or awkward context-awareness (i.e. things like pre/post "dir-change" triggers)
  * Not ideal for software development in many ways

Based on the last point, maybe you're already thinking "Use emacs/vim/eclipse!", but I also
believe that a huge, do-everything IDE is not the True Way.

IPython is great but in many ways is more a framework than a solution, and even though
it does basic shell stuff, out of the box it is not fit for normal use.

  * obviously not completely bash-like (nor should it be): 'cd <dir>' works but 'tail -f <file>' does not
  * lack of consistency: profiles vs. rc-files vs straight programmatic api configuration all gets confusing




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

Smash is built on top of pysh, and actually has very little core functionality. Most of what it does
happens through plugins.  Apart from what the bash/python hybrid features that come from pysh, Smash
also inherits all the flexibility of IPython in terms of I/O hooks and pre/post processing.  So go
nuts with your domain specific language or ruby's pry shell or go attach a lisp-lua-node runtime
onto this frankenstein bananaphone piano, see if I care.





=========================
Generic Plugins for Smash
=========================


Browser Integration:
--------------------
  - manage and open bookmarks globally or per-project

  - performs web searches with http://duckduckgo.com API, allowing for:

    - direct search of stack-overflow, django docs, pypi, etc

Git VCS Integration:
--------------------
  - If applicable, default prompt includes current branch name

  - Tab completion including:

    - Branch completion in all the right spots

    - File-system completion when using 'git mv' or 'git add'

    - smart branch/file-system completion when using 'git diff'

  - Various default aliases and places to put more (making .git/config optional)

Abstractions for project-management:
------------------------------------
  - directories can be registered as Projects

  - Project configuration is stored with JSON

    - you can manipulated it via the command-line or edit config-files yourself

  - Projects can activate their own alias groups that are not shared by the shell at large

  - Project code does not necessarily need to be python, but if it is you get sweet benefits

  - Projects can be watched for changes, triggers for linters can be added, etc

  - code can be searched asynchronously, results delivered in a way that doesnt clutter your screen

  - Projects can be "activated", which might mean convenient side-effects like

     - activating a virtual environment

     - starting a virtual machine

     - opening a web page

     - whatever else you want..




=================================
Python Specific Plugins for Smash
=================================

Virtual-Environments:
---------------------
  - venvs can be activated/deactivated cleanly and without lasting side-effects

  - Project activation (in the sense of the plugin above) can trigger

Fabric integration:
-------------------
  - tab-completion over fabfile commands

  - programmatic access to the functions themselves

  - PS: this plugin is a good example of a minimal "post-dir-change" trigger

Unit tests:
-----------
  - post-dir-change hook finds "tests/" or "tests.py" in working directory

  - or, scan everything under this working-directory or a known Project

  - attempts to detect what type of unittests these are via static analysis (django/vanilla unittest/etc)

  - test files are enumerated and shortcuts for running them quickly are updated





======================
Possible deal-breakers
======================

At this point to use Smash you unfortunately will need IPython==0.10 installed, and even more
unfortunately you probably need it installed at the system level.  (Later versions of IPython are
not compatible `pysh` IPython profile, and I have not gotten around to porting it yet).  You will
likely need it installed at the system level because smash itself aims at managing virtual-envs..
running it from one might be possible but could lead to confusion.

One current limitation of the combination of pysh / ipython / smash is a lack of job control in the
sense that you might be used to.  Specifically you can background tasks with an `&` as usual, but
`fg` does not resume.  At first this seemed horrible but in practice I think this consideration is
not very important- shells are cheap to spawn and a workflow around `screen` works better anyway.




=============
Related Links
=============

  - http://ipython.org/ipython-doc/dev/interactive/shell.html
  - http://faculty.washington.edu/rjl/clawpack-4.x/python/ipythondir/ipythonrc-pysh



============
Other Shells
============

  - xiki (a wiki inspired gui shell) http://xiki.org/
