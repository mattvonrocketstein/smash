---
<a id="list"></a>

[Autojump](#autojump) |
[Handle Command Failure](#hcf) |
[Do What I Mean](#dwim) |
[Change-dir Hooks](#cd-hooks) |
[Python Tools Completion](#ptc) |
[Python Virtual Environments](#virtualenv)

The smash core aims to be small and only include the essentials, so much of the behaviour of shell comes down to plugins.  In Smash, "plugins" are just IPython extensions which require smashlib, and possibly require the smash shell itself.  As a result many of the plugins may work in vanilla IPython.  If you don't care about the built in plugin options and only want to write new plugins, [see this section](#writing-new).  There are a few main things that plugins may potentially do.  Specifically, **each plugin may**:

1. have configuration options
2. publish commands or command aliases
3. add completers or new input preprocessing
4. receive signals from the IPython event subsystem
5. receive signals from the smash-specific event subsystem
6. send signals on the smash-specific event subsystem

The rest of this page attempts to completely describe the plugins which ship with smash, although note that these plugins may not be enabled by default.

<hr/>

####<a id="hcf">Handle Command Failure</a>
This plugin receives a signal whenever a system command fails, where the signal contains information about both the full command and the exit code.  Note that this is happens all the time since "ls /does/not/exist" terminates with a non-zero exit status, but this may interest plugin implementors.

#####Signals

*Receives:* COMMAND_FAIL

-------------------------------------------------------------------------------


--------------------------------------------------------------------------------


##<a id="writing-new">Writing new plugins</a>

Writing new plugins is fairly easy, but may not be necessary for your application (see the [configuration summary](features.html#configuration) or the [main configuration documentation](configuration.html)). If you do need to write a plugin, read on, but first a bit of background.  Smash is built on top of [IPython](http://ipython.org/) and is in fact itself an IPython extension.  *Smash plugins are essentially ipython extensions which require smash*, but it can be useful to differentiate the terminology.  Before going much further it's probably a good idea to check out the existing IPython docs on [writing extensions](http://ipython.org/ipython-doc/dev/config/extensions/).

If you want to do simple stuff like just writing new commands then a tutorials for [writing IPython magic](http://catherinedevlin.blogspot.com/2013/07/ipython-helloworld-magic.html) will probably be all you need.

If you want to get your hooks into smash-specific events like "directory change" or "virtual environment deactived" then read [this documentation](shell_use_cases.html#signals) about the smash event system. For an example of writing new tab-completion stuff, check out [the code for the fabric completer](https://raw.githubusercontent.com/mattvonrocketstein/smash/master/smashlib/plugins/fabric.py).  For an example of input preprocessing see the [code for](#TODO) the [currency converter](#TODO).  For an example of all-else-fails input processing (meaning input was neither bash nor python) see [the code for](https://raw.githubusercontent.com/mattvonrocketstein/smash/master/smashlib/plugins/dwim.py) the [do-what-i-mean plugin](#TODO)

-------------------------------------------------------------------------------
