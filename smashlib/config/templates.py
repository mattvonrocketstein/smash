""" smashlib.config.templates
"""
aliases = """
{
 //default aliases, these are active for all projects
 '__smash__':[
   //['some_alias',    'some_cmd'],
   //['another_alias', 'another_cmd'],
 ]
 //'some_project':[
   //['some_alias','some_cmd'],
 //]
 }
"""

env = """
{
 //default env, these are active for all projects
 '__smash__':[
   //['some_var_name',    'env_var_value'],
   //['another_var_name', 'env_var_value'],
 ]
 //'some_project':[
   //['some_var','another_env_var_value'],
 //]
 }
"""

macros = """
{
 //default macros, these are active for all projects
 '__smash__':[
   //['some_macro_name',    'some_macro_code'],
   //['another_macro_name', 'more_macro_code'],
 ]
 //'some_project':[
   //['some_macro','even_more_macro_code'],
 //]
 }
"""
