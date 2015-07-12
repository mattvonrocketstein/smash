###Writing new plugins

Writing new plugins is fairly easy, but may not be necessary for your application (see the [configuration summary](features.html#configuration) or the [main configuration documentation](configuration.html)). If you do need to write a plugin, read on, but first a bit of background.

###Background

Smash is built on top of [IPython](http://ipython.org/) and is in fact itself an IPython extension.  *Smash plugins are essentially ipython extensions which require smash*, but it can be useful to differentiate the terminology.  Before going much further it's probably a good idea to check out the existing IPython docs on [writing extensions](http://ipython.org/ipython-doc/dev/config/extensions/).

###Resources for reference

If you want to do simple stuff like just writing new commands/macros/magic then a tutorials for [writing IPython magic](http://catherinedevlin.blogspot.com/2013/07/ipython-helloworld-magic.html) will probably be all you need.

* If you want to get your hooks into smash-specific events like "directory change" or "virtual environment deactived" then read [this documentation](shell_use_cases.html#signals) about the smash event system.

* For an example of writing new tab-completion stuff, check out [the code for the fabric completer](https://raw.githubusercontent.com/mattvonrocketstein/smash/master/smashlib/plugins/_fabric.py).

* For an example of input preprocessing see the [code for](#TODO) the [currency converter](#TODO).

* For an example of all-else-fails input processing (meaning input was neither bash nor python) see [the code for](https://raw.githubusercontent.com/mattvonrocketstein/smash/master/smashlib/plugins/dwim.py) the [do-what-i-mean plugin](#TODO)
