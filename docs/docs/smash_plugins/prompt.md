<a id=plugin></a>
### Plugin: Prompt

The smash prompt is configured in the file at `~/.smash/etc/prompt.json` If you have [configured your editor](../configuration#editor) already you can open it by typing `prompt.edit`.

<a id=example-data></a>
### Example data

```json
[
    {"type": "python", "value": "smashlib.prompt.venv","space_margins": true, "color":"purple",},
    {"type": "env", "value": "$USER",},
    {"type": "literal", "value": "@",},
    {"type": "shell", "value": "hostname",},
    {"type": "literal","value": ":",},
    {"type": "python", "value": "smashlib.prompt.working_dir",},
    {"type": "literal", "value": " ",},
    {"type": "python", "value": "smashlib.prompt.git_branch","color" : "blue",},
    {"type": "python", "value": "smashlib.prompt.user_symbol", "color": "red",},
]
```

<a id=components></a>
### Prompt components

The `prompt.json` configuration file consists of a list, where each entry represents an inidividual **prompt component**.  Prompt components are not rendered conditionally, but may return the empty string. Every prompt component entry must contain data for the fields `type` and `value`.  There are only 4 choices for the "type" field, and choosing the type determines the semantics of the "value" field.  See the table below:

| Type    | Value field | Rendered prompt component         |
|---------|---------------------|---------------------------|
| "env"   | "value" field must be the name of a single environment variable (with or without the "$" prefix).  | Renders to the value of the variable |
| "shell" | "value" field is a shell command to run.  Note that environment variables may be used | Renders the result of executing the shell command |
| "literal" | "value" field is a simple string | Renders the simple string, no interpretation or interpolation |
| "python" | "value" field is a python dot-path which corresponds to a callable function of zero arguments | Renders to whatever the python function returns

### Built-in prompt components

Several pre-built prompt components are already written in python.  See the table below for a description of each.
