#!/usr/bin/env python
""" triple2hash.py

    crude script to convert docstrings from python function definitions to
    hash-style comments.  this only works on single-line comments.  why would
    anyone want to do this, you ask?  sometimes unittests run with --verbosity=2
    show docstrings stuff in the output.. in order to associate that information
    with the actual function, you'd have to search for the function with that
    docstring, which is maddening.

    with a more sophisticated usage of re this could be adapted to multi-line
    comments, but the idea is that enough effort went into a multi-line comment
    that it might be better to just leave them alone and deal with it by hand.

    the output of the conversion for the file used as an argument will go to stdout.

    USAGE:
      $ triple2hash.py <filename>
"""
import re
import sys

class ConvertComments(object):
    def __init__(self, fname):
        self.fname = fname

    def __call__(self):
        self.doit(open(self.fname).read())

    @staticmethod
    def helper(token, peek, lines, index):
        start = peek.find(token)
        replacement = '#' if peek.strip().startswith(token+' ') else '# '
        peek = ''.join(list(peek))
        peek = list(peek)
        peek.insert(start, replacement)
        peek = ''.join(peek)
        peek = peek.replace(token, '').rstrip()
        lines[index] = peek

    def is_func_def(self, line):
        func_def = re.compile('\s*def .*')
        return func_def.match(line)

    def doit(self, S):
        lines = S.split('\n')
        for i in range(len(lines)):
            line = lines[i]
            print line
            if self.is_func_def(line):
                try: peek = lines[i+1]
                except IndexError: continue
                else:
                    clean = peek.strip()

                    test = lambda token, clean: all([clean.startswith(token),
                                                     clean.endswith(token),
                                                     clean!=token])
                    token = '"""'
                    if test(token, clean): self.helper(token, peek, lines, i+1)

                    token = "'''"
                    if test(token, clean): self.helper(token, peek, lines, i+1)

if __name__=='__main__':
    converter = ConvertComments(sys.argv[1])
    converter()
