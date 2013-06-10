import re
def split_on_unquoted_semicolons(txt):
    PATTERN = re.compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')
    return PATTERN.split(txt)[1::2]
def test_split_on_unquoted_semicolons():
    from smashlib.util import split_on_unquoted_semicolons
    data = '''part 1;"this is ; part 2;";'this is ; part 3';part 4;this "is ; part" 5'''
    assert split_on_unquoted_semicolons(data)==['part 1', '"this is ; part 2;"', "'this is ; part 3'", 'part 4', 'this "is ; part" 5']

