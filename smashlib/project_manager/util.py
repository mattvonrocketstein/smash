""" smashlib.project_manager.util
"""
def clean_project_name(name):
    return name.replace('-','_').replace('.', '_')

class UnknownProjectError(Exception):
    pass
