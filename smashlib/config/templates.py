""" smashlib.config.templates
"""
plugins = """
//
// A list of strings, representing the enabled plugins.
// By convention, if plugins have additional configuration, that
// is held in separate json at ~/.smash/etc/<plugin_name>_conf.json
//
// Individual strings represent importable python modules that hold plugins.
//
[
]
"""

aliases = """
{
 // Default aliases, these are active for all projects
 '__smash__': [
   // ['some_alias',    'some_cmd'],
   // ['another_alias', 'another_cmd'],
 ],
 // 'some_project': [
 //   ['some_alias','some_cmd'],
 // ]
 }
"""

env = """
{
 // Default environment variables, these are active for all projects
 '__smash__':[
   // ['some_var_name',    'env_var_value'],
   // ['another_var_name', 'env_var_value'],
 ]
 // 'some_project':[
 //    ['some_var','another_env_var_value'],
 // ]
 }
"""

venvs = """
//
// Default map from project-names to project virtualenvironments.
//
// Expected schema is simply {'project_name':'venv_path'},
// where project-names are strings representing NAMES not paths,
// and paths are absolute paths to a python virtual-environment.
//
// Paths expansion is used, i.e. ~ is allowed.
//
{
 // 'project_name': virtual_environment_directory,
 }
"""

macros = """
{
 // Default macros, these are active for all projects
 '__smash__':[
   // ['some_macro_name',    'some_macro_code'],
   // ['another_macro_name', 'more_macro_code'],
 ],
 // 'some_project':[
 //    ['some_macro','even_more_macro_code'],
 // ]
 }
"""
