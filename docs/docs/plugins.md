---
<a id="list"></a>

[Liquidprompt](#liquidprompt) |
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



####<a id="hcf">Handle Command Failure</a>
This plugin receives a signal whenever a system command fails, where the signal contains information about both the full command and the exit code.  Note that this is happens all the time since "ls /does/not/exist" terminates with a non-zero exit status, but this may interest plugins.

#####Signals

*Receives:* COMMAND_FAIL


<a id="ptc"></a>
####Python Tools Completion

This plugin provides completion options for common python tools like [Fabric](#), [IPython](#), [setup.py](#), [flake8](#)/[pyflakes](#) [tox](#), and other stuff you probably use on a daily basis.  Completion for each command is at least over command line options/flags, but in some cases there are other context clues that can be provided:

* fabric completion also works over task names.
* tox completion includes available environments according to tox.ini when using "tox -e"
* ipython completion includes available profiles when using --profile option

#####Configuration Options:
* `PythonTools.verbose`: set True to see debug messages

-------------------------------------------------------------------------------

####<a id="autojump">Autojump</a>
Smash ships with an integrated version of the wonderful [autojump](https://github.com/joelthelion/autojump) command line tool, which uses information from change-dir to maintain a ranked list of flexible short cuts.  In other words after you've cd'd into /foo/bar/baz/qux at least once, you can use `j qux` or `jump qux` to take you there afterwards.  Tab completion over jump-destinations is automatically enabled so that `j qu<TAB>` does what you'd expect.

#####Commands:
* `j some_bookmark`: jump to a directory based on the weighted ratings in the current database

#####Configuration Options:
* `_.AutoJump.verbose`: set True to see debug messages

#####Signals

*Receives:* CHANGE_DIR

-------------------------------------------------------------------------------

####<a id="liquidprompt">Liquidprompt</a>

This plugin provides prompt rendering via the wonderfully dynamic [liquidprompt tool](#https://github.com/nojhan/liquidprompt).  Liquidprompt has rich options for configuration and it's recommended that you [configure it in the normal way](https://github.com/nojhan/liquidprompt#features-configuration), but, some of these options can be overridden from `~/.smash/config.py` (see below).

#####Commands:
* `prompt_tag "my tag"`: add a text prefix for the current prompt

#####Configuration Options:
* `_.LiquidPrompt.verbose`: set True to see debug messages
* `_.LiquidPrompt.float`: set True to insert more space around prompt
* `_.LiquidPrompt.prompt_append`: set a suffix on the prompt ('\n>' is a good one for legibility)

#####Signals

*Receives:* UPDATE_PROMPT_REQUEST

-------------------------------------------------------------------------------

####<a id="autojump">Enhanced "which"</a>

This plugin replaces the system "which" command.

#####Commands:
* `which *module_or_cmd*`: display information about a system command or python module


-------------------------------------------------------------------------------


####<a id="cd-hooks">Change directory hooks</a>

The CD hooks feature is mostly a service for other plugins to use. It adds a "directory changed" event to smash, which is useful for building stuff like automatic-activation rules (see for example the [project manager](project_manager.html).  New plugins can build hooks and subscribe to CD events, or you can just register a callback without writing a new plugin.  Here's a minimal example of what a callback would look like:

~~~~{.python}
    def test_change_message(bus, new, old):
        """ a demo for the CD hook """
        print 'moved from old directory {0} to new one at {1}'.format(old, new)
~~~~

#####Configuration Options:
* `ChangeDirHooks.verbose`: set True to see debug messages
* `ChangeDirHooks.change_dir_hooks.append('foo)`: add python dot-paths or shell commands as cd-hooks

#####Signals
*Publishes:* CHANGE_DIR

-------------------------------------------------------------------------------


####<a id="dwim">Do What I mean</a>

<a id="dwim-suffix"></a>
The DoWhatIMean plugin supports zsh-style alias suffixes, automatic directory changing, opening of urls, etc.  For a feature summary, see the input -> action list below.

| On Input             | Run test                          | If test is true Action is  |
| -------------------- |---------------------------------- | -------------------------- |
| http://foo/bar       | *(none)*                          | open with browser          |
| ftp://foo/bar        | *(none)*                          | open with browser          |
| ssh://user@host      | *(none)*                          | run ssh                    |
| mosh://user@host     | *(none)*                          | run mosh                   |
| foo.bar              | is foo.bar executable?            | run as usual               |
| foo.bar              | is bar a defined suffix_alias?    | open with specified opener |
| foo/bar              | is bar a directory?               | change-dir to bar          |
| foo/bar              | is bar editable?                  | open with editor           |
| foo/bar:ROW:COL:     | is bar editable?                  | open with editor           |

#####Configuration Options:
* `DoWhatIMean.verbose`: set True to see debug messages
* `DoWhatIMean.suffix_aliases`: map of `{file_extension -> open_command}`

#####Signals

*Receives:* URL_INPUT, FILE_INPUT

-------------------------------------------------------------------------------

####<a id="virtualenv">Virtual Environment</a>

Smash has sophisticated virtualenv support which is useful particularly if you're working on multiple projects or working with multiple versions of the same requirements.  Activating/deactivating venvs is done with `venv_activate some_dir` and `venv_deactivate`, respectively.  This not only updates your $PATH, but updates the python runtime.  Modules from the new environment can now be imported directly, and side-effects from the old virtualenv are purged.  To activate and deactivate virtualenv's automatically, take a look at the [project manager documentation](/project_manager.html).

#####Commands:
* `venv_activate some_dir`: activate a specific virtual environment
* `venv_deactivate some_dir`: deactivates the current virtual environment

#####Configuration Options:
* `VirtualEnv.verbose`: set True to see debug messages

#####Signals

--------------------------------------------------------------------------------


##<a id="writing-new">Writing new plugins</a>

Writing new plugins is fairly easy, but may not be necessary for your application (see the [configuration summary](features.html#configuration) or the [main configuration documentation](configuration.html)). If you do need to write a plugin, read on, but first a bit of background.  Smash is built on top of [IPython](http://ipython.org/) and is in fact itself an IPython extension.  *Smash plugins are essentially ipython extensions which require smash*, but it can be useful to differentiate the terminology.  Before going much further it's probably a good idea to check out the existing IPython docs on [writing extensions](http://ipython.org/ipython-doc/dev/config/extensions/).

If you want to do simple stuff like just writing new commands then a tutorials for [writing IPython magic](http://catherinedevlin.blogspot.com/2013/07/ipython-helloworld-magic.html) will probably be all you need.

If you want to get your hooks into smash-specific events like "directory change" or "virtual environment deactived" then read [this documentation](shell_use_cases.html#signals) about the smash event system. For an example of writing new tab-completion stuff, check out [the code for the fabric completer](https://raw.githubusercontent.com/mattvonrocketstein/smash/master/smashlib/plugins/fabric.py).  For an example of input preprocessing see the [code for](#TODO) the [currency converter](#TODO).  For an example of all-else-fails input processing (meaning input was neither bash nor python) see [the code for](https://raw.githubusercontent.com/mattvonrocketstein/smash/master/smashlib/plugins/dwim.py) the [do-what-i-mean plugin](#TODO)

-------------------------------------------------------------------------------
