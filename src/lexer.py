"""This file contains the lexer rules and the list of valid tokens."""

import lex
import sys
import re


# This is the list of token names.
tokens = (
    'INT', 
    'FLOAT', 
    'STRING',
    'SYMBOL',
    'LPAREN', 
    'RPAREN'
)

# These are regular expression rules for simple tokens.
t_LPAREN    = r'\('
t_RPAREN    = r'\)'

# Read in a float.  This rule has to be done before the int rule.
def t_FLOAT(t):
    r'-?\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t

# Read in an int.
def t_INT(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

# Read in a string, as in C.  The following backslash sequences have their 
# usual special meaning: \", \\, \n, and \t.
def t_STRING(t):
    r'\"([^\\"]|(\\.))*\"'
    escaped = 0
    str = t.value[1:-1]
    new_str = ""
    for i in range(0, len(str)):
        c = str[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c
    t.value = new_str
    return t

# Ignore comments.
def t_comment(t):
    r'[#][^\n]*'
    pass

# Track line numbers.
def t_newline(t):
    r'\n+'
    t.lineno += len(t.value)

# Read in a symbol.  This rule must be practically last since there are so few
# rules concerning what constitutes a symbol.
def t_SYMBOL(t):
    r'[^0-9()][^()\ \t\n]*'
    return t

# These are the things that should be ignored.
t_ignore = ' \t'

# Handle errors.
def t_error(t):
    raise SyntaxError("syntax error on line %d near '%s'" % 
        (t.lineno, t.value))

# Build the lexer.
lex.lex()


# The following is for testing:
def _internal_tests():
    tests = [
        ("(", "LPAREN", "("),
        (")", "RPAREN", ")"),
        ("1234", "INT", 1234),
        ("-1234", "INT", -1234),
        ("1.", "FLOAT", 1.0),
        ("-1.", "FLOAT", -1.0),
        ("0.1", "FLOAT", 0.1),
        ("0.1e-1", "FLOAT", 0.1e-1),
        (r'""', "STRING", ""),
        (r'"foo"', "STRING", "foo"),
        (r'"\""', "STRING", '"'),
        (r'"\n\t\"\\"', "STRING", "\n\t\"\\"),
        ("#1.0\n(", "LPAREN", "("),
        ("\n\n(", "LPAREN", "("),
        ("&1", "SYMBOL", "&1"),
        ("-", "SYMBOL", "-")
    ]
    for i in tests:
        (s, type, value) = i 
        lex.input(s)
        tok = lex.token()
        try:
            assert tok.type == type
            assert tok.value == value
            assert not lex.token()
        except AssertionError, e:
            sys.stderr.write("squeamish: test failed: %s led to %s\n" % (
                `i`, tok))
            raise AssertionError

def _external_tests():
    while 1:
        try:
            s = raw_input("squeamish> ")
        except EOFError:
            break
        if not s:
            continue
        lex.input(s)
        while 1:
            tok = lex.token()
            if tok:
                print `tok`
            else: 
                break


# Do some testing.
if __name__ == '__main__':
    _internal_tests()
    _external_tests()
