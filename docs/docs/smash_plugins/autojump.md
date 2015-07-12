<a id="autojump"></a>
### Plugin: Autojump

Smash ships with an integrated version of the wonderful [autojump](https://github.com/joelthelion/autojump) command line tool, which uses information from change-dir to maintain a ranked list of flexible short cuts.  In other words after you've cd'd into /foo/bar/baz/qux at least once, you can use `j qux` or `jump qux` to take you there afterwards.  Tab completion over jump-destinations is automatically enabled so that `j qu<TAB>` does what you'd expect.

#####Commands:
* `j some_bookmark`: jump to a directory based on the weighted ratings in the current database

#####Signals

*Receives:* CHANGE_DIR
