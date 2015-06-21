Smash configuration, like smash libraries and executables, are stored in `~/.smash`.  The main configuration file is `~/.smash/etc/config.py`.  If your [editor is configured](#editor), you can open the main configuration file at any time from typing `ed_config` inside of smash.

<a id="inheritance-shell"></a><a id="inheritance"></a>
####Inheriting existing shell configuration
By default smash will try to honor existing bash aliases and functions.  If you do not want your bash aliases migrated into Smash, ensure the `load_bash_aliases` settings is False.

~~~~{.python}
    Smash.load_bash_aliases = False
~~~~

If you do not want to be able to run legacy bash functions from your shell, ensure the `load_bash_functions` setting is False.  Note that only bash functions mentioned in your profile, .bashrc, etc will be loaded.  (Loading bash functions from arbitrary files that you source is [issue #15](https://github.com/mattvonrocketstein/smash/issues))

~~~~{.python}
    Smash.load_bash_functions = False
~~~~


<a id="inheritance-ipython"></a>
####Inheriting existing IPython configuration
If you are already using IPython and want to load aspects of existing profile configuration, add something like this to `~/.smash/config.py`:

~~~~{.python}
    load_subconfig('ipython_config.py', profile='default')
~~~~


<a id="editor"></a>
####Editor configuration
There are several reasons that it can be useful to let smash know about your editor.  Here are a few:

* Smash, like IPython, helps you open and edit the code for any given object.  (try: `import webbrowser; ed webbrowser`).
* Zsh-style [suffix aliases](plugins.html#dwim-suffix) are supported by the [DWIM plugin](plugins.html#dwim)
* various shortcuts help you open smash configuration: `ed_editor`, `ed_aliases`, etc

The editor configuration file (`~/.smash/etc/editor.json`) should have the following format, otherwise the json validator will complain:

~~~~{.json}
 {
   "console":"some_editor_invocation",
   "window_env":"some_editor_invocation"
 }
~~~~

If this file does not exist, it will be created for you with default values.  Note that invocation lines may include flags, for instance *emacsclient -n* or  *nano --softwrap --quiet* is fine.

<a id="aliases"></a>
####Alias configuration

In smash aliases are essentially the same as ipython or bash aliases, except that these aliases are potentially project specific.  The alias configuration file (`~/.smash/etc/aliases.json`) will be created if it does not exist, and should have a format similar to the following example, or else the json validator will complain.

~~~~{.json}
{ "__smash__":
    [ ["bunzip"," bunzip2"],
      ["l", "ls -la --color"],
      .....
    ],
  "my_first_project":
    [ ["go", "start-daemon&"],
      ["stop", "kill -KILL `cat daemon.pid`"]
    ],
  "other_project":
    [ ["go", "sudo /etc/init.d/mongo start"],
      ["stop", "sudo /etc/init.d/mongo stop"],
      ...
    ],
  ...
}
~~~~

**The aliases mentioned in the `__smash__` section are global and always-on, so this is most likely where you want to put your default aliases.**  The aliases mentioned in "my_first_project" and "other_project" would only be activated when that project was activated.  See the [project manager documentation](project_manager.html) for a more in-depth explanation of projects.
