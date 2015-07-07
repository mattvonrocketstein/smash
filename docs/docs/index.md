<a id="about"></a>
##What is it?

Smash is a smarter shell.  [Python developers](Python_use_cases.html) will be particularly interested because it also happens to host a full-fledged Python runtime (via IPython) and offers sophisticated support for Python virtual environments.  Smash leverages existing system tab completion setup as well as allowing variable & keyword completion in Python namespaces.  For extensions, Smash provides a powerful and flexible [plugin architecture](plugins.html) that is easy to use.

If you're not a pythonista, then you can safely ignore the python stuff and perhaps benefit from other features like [project management](project_manager.html), an [event and hook system](#), a self-contained install with no root required, and JSON-based [configuration files](configuration.html).

<a id="requirements"></a>
##Requirements

You'll need git in order for the smash bootstrap to clone the smash repo.  Also virtualenv, and the usual Python development prerequisites.  You need to be able to compile at least fairly simple C code (this is due to smash's reliance on [fabric](#)).  In debian-based linux, the following one-liner should do the trick and for OSX you can probably homebrew something similar.

~~~~{.bash}
  $ sudo apt-get install git-core Python-virtualenv Python-dev build-essential
~~~~

<a id="quickstart"></a>
##Quickstart

The smash installation happens in a sandbox, does not require root, and will not interefere with any existing system versions of IPython.  The cost of this is that setup is a little bit nonstandard and `setup.py` should not be used directly unless you only want to develop against the support libraries (for that see: [dev installation](#dev-installation))

~~~~{.bash}
  $ export SMASH_BRANCH=master
  $ export SMASH_URL=https://raw.githubusercontent.com/mattvonrocketstein/smash/$SMASH_BRANCH/bootstrap.sh
  $ curl $SMASH_URL|bash
  $ ~/bin/smash
~~~~

Don't like the idea of curling random instructions?  If the above installation method seems scary to you, here's more or less what the bootstrap.sh file is accomplishing:

~~~~{.bash}
  $ git clone https://github.com/mattvonrocketstein/smash.git
  $ mv smash ~/.smash
  $ cd ~/.smash
  $ virtualenv . --no-site-packages
  $ source bin/activate
  $ pip install -r install_requirements.txt
  $ python install.py
~~~~


<a id="dev-installation"></a>
##Installation for development

There are two parts to Smash: smashlib and the smash shell.  Smashlib by itself might be useful as support code for other work.  The instructions in the [quickstart section](#quickstart) will install both the shell and the support library.  Installing the shell is atypical for the reasons mentioned in that section, but **if you only want to develop against smashlib**, installation is  standard:

```shell
  $ git clone https://github.com/mattvonrocketstein/smashlib.git
  $ cd smashlib
  $ Python setup.py develop
  $ pip install -r requirements.txt
```

Smash is in beta currently and has no major release versions apart from "master" and "experimental".  If you want to install a particular version of smash, the thing is to use the quickstart instructions, but specify a branch hash:

~~~~{.bash}
  $ SMASH_BRANCH=mainline curl https://raw.githubusercontent.com/mattvonrocketstein/smash/master/bootstrap.sh | bash
~~~~

<a id="dev-installation"></a>
##Philosophy

**But Why?**
So, *why build yet another shell?*  Put simply, shells still kind of suck.  The main problem is that classic shells are inflexible and difficult to extend.  If you do manage to extend them at all, then you probably had to do it with shell code and the result is something that's fragile, difficult to read, and difficult to maintain.

Just for the sake of an examples, let's consider the problem of a "do what I mean" extension for your shell, where if you type something that looks like a url then the url is opened automatically for you.  To effect a pre-exec style hook in bash, you'll probably need [black magic](http://www.twistedmatrix.com/users/glyph/preexec.bash.txt) with the `DEBUG` trap (ugh).  Zsh is much better and has a built in pre-exec hook, but of course you'll still be writing (or at least invoking) your hooks in shell code.  This works at first, but things start to get messy when issues of code-reuse come up, or if you want to [invoke hooks conditionally](project_manager.html), etc.

If you still think the do-what-i-mean puzzle sounds easy to solve in your shell, how about colorizing all structured data (maybe json or server logs) sent to stdout regardless of whether that data comes from "cat" or "echo" without explicit pipes?  What about the possibility of cohosting not just python, but other arbitrary foreign REPLs alongside your shell?  At least in theory Smash could allow simultaneous and unambiguous usage of tools for sql, ruby, mongo, lisp, whatever.  Or, what if embedding your whole system shell into [an interactive webpage was trivial?](http://iPython.org/videos.html#the-iPython-notebook)

Eventually shells and shell-extensions get so complex they [grow their own package managers](https://github.com/robbyrussell/oh-my-zsh).  Why bother when a modern full-fledged programmingly language is bound to have real package management options anyway?  Honestly there's a reason we don't usually write [socket code in shell script](http://www.lainoox.com/bash-socket-programming/), and a reason why system administration has moved so far away from the bad old days where any configuration management that was automated at all was automated with hacky shell scripts.  *But*, since you might have existing shell aliases or functions that you still depend on, smash tries to help you [access your legacy junk](configuration.html#inheritance-shell) until you can port it.

SmaSh's close integration with Python itself is a huge plus, but it's also just a side effect of fixing the main problems around making a shell that is truly flexible and nontrivially extensible.

**Design goals**

0. Single-step idiot proof installation
1. The installation should always be inside a virtualenvironment, and never require root
2. Try to maintain compatability with pre-existing setup for zsh and bash.
3. Everything is a plugin!  Core functionality is small as hell and (almost) everything is optional
4. Zero (initial) configuration and sane defaults. Only power users have to care about how configuration actually works
5. Python developers should be able to have a stable and persistent shell.  No kill/restart to clean namespaces, etc, regardless of how many projects they work on at once.
6. Try to honor and maintain compatability with any pre-existing IPython configuration.
7. Eventually, non-Python developers with an addiction to a particular REPL should be able co-host that REPL alongside their system shell.
8. Tight integration with shell and a very powerful/flexible project-management abstraction
