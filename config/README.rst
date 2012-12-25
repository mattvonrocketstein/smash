
plugins.json
-------------

Describes known SmaSh plugins.  This json file maps every plugin
name to settings for that plugin.  By default, the only setting is
"enabled", set to 1 if True otherwise set to 0 if False.  If a plugin
has complex settings, it should have it's own settings file, but to
avoid every plugin having such a file, feel free to put simple stuff
here.

editor.json
------------

Holds two settings for editor.. one to be used if SmaSh is running
in a console environment, one to be used in a windowing system.

projects.json
--------------

This file describes projects, directories to load projects from.
Additionally it can describe generic aliases or per-project aliases,
and pre/post-activation rules for individual projects.
