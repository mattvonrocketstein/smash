title: Use Cases: Shell
menu-position: 2
---

This section is just an overview.  You could also jump directly to the plugin documentation for the relevant plugins: [Liquidprompt](#liquidprompt), [Autojump](#autojump), [Do What I Mean](#dwim), or [Change-dir Hooks](#cd-hooks).


-------------------------------------------------------------------------------

####<a href="#signals">Shell signals/events system</a>

Plugin authors may wish to subscribe to various smash events to extend smash's functionality.  The smash event system will send signals for all the scenarios described below.


| Signal Name           | Signal Description                                                    |
| ----------------------|---------------------------------------------------------------------- |
| CHANGE_DIR            | Issued on 'cd' or 'pushd', etc                                        |
| POST_RUN_INPUT        | Issued after user input has been processed (raw input)                |
| POST_RUN_CELL         | Issued after user input has been processed (transformed input)        |
| COMMAND_FAIL          | Issued when a system command ("ls non_existant_directory") has failed |
| FILE_INPUT            | Issued whenever user input looks like a file path                     |
| URL_INPUT             | Issued whenever user input looks like a URL                           |
| UPDATE_PROMPT_REQUEST | Can be issued to request that prompt is redrawn                       |
| DOT_CMD               | Issued when user input starts with "." but is not a file name         |
| SMASH_INIT_COMPLETE   | Issued when smash is completely bootstrapped                          |

Signal payloads and current subscribers (if any) are described in the table below.

| Signal Name           | Signal Payload             | Subscribers                              |
| ----------------------|----------------------------|----------------------------------------- |
| CHANGE_DIR            | (new_dir, old_dir)         | <a href=plugins.html#autojump>autojump</a> |
| POST_RUN_INPUT        | last input *(raw)*           | <a href=plugins.html#post_input>post_input</a>|
| POST_RUN_CELL         | last_input *(transformed)*   | *None*                 |
| COMMAND_FAIL          | (last_command, error_code) | <a href=plugins.html#handle_command_failure>handle_command_failure</a> |
| FILE_INPUT            | file_path                  | <a href=plugins.html#dwim>dwim</a> |
| URL_INPUT             | url                        | <a href=plugins.html#dwim>dwim</a> |
| UPDATE_PROMPT_REQUEST | new_prompt                 | <a href=plugins.html#liquidprompt>liquidprompt</a> |
| DOT_CMD               | dot_cmd                    | <a href=project_manager.html>project manager</a> |
| SMASH_INIT_COMPLETE   | *None*                     | *all* |

####<a id="considerations">Command Considerations</a>

To avoid conflicting with python namespaces, system commands that involve period (`.`) will be translated to use an underscore (`_`) instead.  Any system command invocations that use a hyphen (`-`) should work normally.

####<a id="shell-problems">Shell-related Problems</a>

Most shell stuff "just works", even when it looks like the grammar for shell vs. python might be ambiguous (for instance, try: `[ string ] && echo its true || echo its false`).  In the event of name collisions, the python namespace typically has preference over the system commands, but this is easy to fix by just deleting the python shadow:

~~~~{.bash}
    smash$ ls
    file1     file2     file3     file4
    file5     file6     file7     file8

    smash$ ls="python namespace shadow"
    smash$ ls
    Out[3]: "python namespace shadow"

    smash$ del ls
    smash$ ls
    file1     file2     file3     file4
    file5     file6     file7     file8
~~~~

If things aren't just working, file an issue or maybe try **IPython's various built-ins**:  The `%%bash` magic might be useful for pasting lots of lines.  The desperate or the paranoid can always prefix commands like `! ls` to ensure they go straight to shell and are not interpretted as python.    Out of the box IPython even supports some limited [mixed python/bash programming](#).
