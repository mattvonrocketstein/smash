<a id="cd-hooks"></a>
###Change directory hooks

The CD hooks feature is mostly a service for other plugins to use. It adds a "directory changed" event to smash, which is useful for building stuff like automatic-activation rules (see for example the [project manager](project_manager.html).  New plugins can build hooks and subscribe to CD events, or you can just register a callback without writing a new plugin.  Here's a minimal example of what a callback would look like:

~~~~{.python}
    def test_change_message(bus, new, old):
        """ a demo for the CD hook """
        print 'moved from old directory {0} to new one at {1}'.format(old, new)
~~~~

###Configuration Options:
* `ChangeDirHooks.verbose`: set True to see debug messages
* `ChangeDirHooks.change_dir_hooks.append('foo)`: add python dot-paths or shell commands as cd-hooks

###Signals
*Publishes:* CHANGE_DIR
