<a id="virtualenv"></a>
###Virtual Environment

Smash has sophisticated virtualenv support which is useful particularly if you're working on multiple projects or working with multiple versions of the same requirements.

Activating/deactivating venvs is done with `venv_activate some_dir` and `venv_deactivate`, respectively.  This not only updates your $PATH, but updates the python runtime.  Modules from the new environment can now be imported directly, and side-effects from the old virtualenv are purged.  To activate and deactivate virtualenv's automatically, take a look at the [project manager documentation](/project_manager.html).

###Commands:
* `venv_activate some_dir`: activate a specific virtual environment
* `venv_deactivate some_dir`: deactivates the current virtual environment

###Configuration Options:
* `VirtualEnv.verbose`: set True to see debug messages

###Signals
* If you're using this plugin in combination with
* post_activate
* pre_activate
* post_deactivate
* pre_deactivate
