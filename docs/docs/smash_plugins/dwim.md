<a id="dwim"></a>
### Plugin: DWIM

<a id="dwim-suffix"></a>
The Do What I Mean plugin supports zsh-style alias suffixes, automatic directory changing, opening of urls, etc.  For a feature summary, see the input -> action list below.

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

###Configuration Options:
* `DoWhatIMean.verbose`: set True to see debug messages
* `DoWhatIMean.suffix_aliases`: map of `{file_extension -> open_command}`

###Signals

*Receives:* URL_INPUT, FILE_INPUT
