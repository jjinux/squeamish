"""This file contains a dictionary of builtins.

Builtins are somewhere between user-defined functions and external functions.
Like external functions, they are written in Python.  Like user-defined 
functions, they can take advantage of lazy evaluation.  However, since they
are written in Python, lazy evaluation is done manually.  Namely, each
parameter is itself a function.  To use that parameter, it must be called in
order to evaluate it.  It's actually the return value of the call that
represents the value of the parameter.  Calling a parameter multiple times is
fine.  The real work of evaluation only happens on the first call, as you'd
expect with lazy evaluation.

Hence, just change:

    def add(a, b): return a + b

to:

    def add(a, b): return a() + b()

"""

import operator
import sys

from Parameter import Parameter
from Expression import Expression
from Symbol import Symbol


def builtin_eq(a, b): return a() == b()
def builtin_ne(a, b): return a() != b()
def builtin_ge(a, b): return a() >= b()
def builtin_le(a, b): return a() <= b()
def builtin_gt(a, b): return a() > b()
def builtin_lt(a, b): return a() < b()
def builtin_add(*args): return _lazy_reduce(operator.add, args)
def builtin_mul(*args): return _lazy_reduce(operator.mul, args)
def builtin_div(a, b): return a() / b()
def builtin_truediv(a, b): return operator.truediv(a(), b())
def builtin_mod(a, b): return a() % b()
def builtin_and(*args): return _lazy_reduce(operator.__and__, args)
def builtin_or(*args): return _lazy_reduce(operator.__or__, args)
def builtin_xor(a, b): return operator.xor(a(), b())
def builtin_not(n): return not n()
def builtin_inv(n): return ~n()
def builtin_lshift(n, count): return n() << count()
def builtin_rshift(n, count): return n() >> count()
def builtin_unval(*args): return [i() for i in args]
def builtin_print(*args): sys.stdout.write(" ".join(_lazy_map(str, args)))
def builtin_abs(n): return abs(n())
def builtin_getitem(obj, i): return obj()[i()]
def builtin_getslice(obj, i, j): return obj()[i():j()]
def builtin_setitem(obj, i, value): obj()[i()] = value(); return value()
def builtin_setslice(obj, i, j, vals): obj()[i():j()] = vals(); return vals()
def builtin_in(obj, element): return element() in obj() 
def builtin_delitem(obj, i): del obj()[i()]
def builtin_delslice(obj, i, j): del obj()[i():j()]
def builtin_len(obj): return len(obj())

def builtin_sub(*args): 
    """This is for either standard subtraction or unary minus."""
    if len(args) == 1: 
        return -args[0]()
    first, others = args[0], args[1:]
    return first() - _lazy_reduce(operator.add, others)

def builtin_if(*args):
    """Lazily interpret the arguments to implement if/elif/else.

    (if test value
     elif test value
     else value)

    elif, else - These are just builtin symbols whose values are strings.
    These keywords will only have special meaning in this function.  In fact,
    the user could even just use string literals ;)

    test - This may be anything that returns a value, including a function
    call, of course.

    value - This will be evaluated if the associated test is true or if it is
    assoicated with an else.  It will be evaluated in a manner similar to the
    body of a function (see Parameter.__call__).

    Here's an example:

    (= wages
      (if (is_hourly worker) (
        (print "How much do you make per hour? ")
        (float (raw_input))
      ) else (
        (print "How much do you make per year? ")
        (float (raw_input))
      ))
    )

    """
    (test, value, args) = args[0], args[1], args[2:]
    if test():
        return value(implicitUnval=1, implicitLast=1)
    while len(args):
        (keyword, args) = args[0], args[1:]
        if keyword() == "elif": 
            (test, value, args) = args[0], args[1], args[2:]
            if test():
                return value(implicitUnval=1, implicitLast=1)
        elif keyword() == "else":
            if len(args) != 1: 
                raise SyntaxError("unexpected values after else")
            value = args[0]
            return value(implicitUnval=1, implicitLast=1)
        else:
            raise SyntaxError("'%s' is neither elif or else" % keyword)

def builtin_dict(*args):
    """Create a dict, and return it.

    Break up args into pairs that are treated as keys and values.

    """
    if len(args) % 2:
        raise SyntaxError("odd number of arguments to function")
    dict = {}
    for i in range(0, len(args), 2):
        key, value = args[i], args[i+1]
        dict[key()] = value()
    return dict

def _lazy_reduce(f, list, init=None):
    """Do a version of reduce that evaluates the members of list lazily.""" 
    list_len = len(list)
    if list_len == 0:
        if init:
            return init
        raise TypeError( "reduce() of empty sequence with no initial value")
    first = list[0]()
    if list_len == 1:
        if init:
            return f(first, init)
        return first
    return f(first, _lazy_reduce(f, list[1:], init))

def _lazy_map(f, list):
    """Do a version of map that evaluates the members of list lazily."""
    return [f(i()) for i in list]

builtins = {
    "==": builtin_eq,
    "!=": builtin_ne,
    ">=": builtin_ge,
    "<=": builtin_le,
    ">": builtin_gt,
    "<": builtin_lt,
    "+": builtin_add,
    "-": builtin_sub,
    "*": builtin_mul,
    "/": builtin_div,
    "truediv": builtin_truediv,
    "%": builtin_mod,
    "and": builtin_and,
    "or": builtin_or,
    "xor": builtin_xor,
    "not": builtin_not,
    "~": builtin_inv,
    "<<": builtin_lshift,
    ">>": builtin_rshift,
    "'": builtin_unval,
    "print": builtin_print,
    "if": builtin_if,
    "elif": "elif",
    "else": "else",
    "abs": builtin_abs,
    "[]": builtin_getitem,
    "[:]": builtin_getslice,
    "[]=": builtin_setitem,
    "[:]=": builtin_setslice,
    "in": builtin_in,
    "del[]": builtin_delitem,
    "del[:]": builtin_delslice,
    "len": builtin_len,
    "{}": builtin_dict
}


# The following is for testing:
def _zero(): return 0
def _one(): return 1
def _elif(): return "elif"
def _else(): return "else"
def _inc(n): return n + 1

def _test_lazy_reduce():
    assert _lazy_reduce(operator.add, [], "foo") == "foo"
    assert _lazy_reduce(operator.add, [_one]) == 1
    assert _lazy_reduce(operator.add, [_one], 1) == 2
    assert _lazy_reduce(operator.add, [_one] * 2) == 2
    assert _lazy_reduce(operator.add, [_one] * 10) == 10
    
def _test_lazy_map():    
    assert _lazy_map(_inc, [_one, _one]) == [2, 2]

def _test_sub():
    assert builtin_sub(_one) == -1
    assert builtin_sub(_one, _one, _one) == -1
    
def _test_if():
    from Environ import Environ # Circular dependency.
    environ = Environ()
    p = lambda parseTree, environ = environ: Parameter(
        value = Expression(environ = environ, parseTree = parseTree))
    _two = p(2)
    _one_two_list = p([1, 2])
    _bad = p(Symbol(name = "undefined"))
    tests = [
        ([_one, _two], 2),
        ([_one, _one_two_list], 2),
        ([_zero, _bad, _elif, _one, _two], 2),
        ([_zero, _bad, _elif, _zero, _bad, _elif, _one, _two], 2),
        ([_zero, _bad, _else, _two], 2)
    ]
    for i in tests:
        (args, value) = i
        try:
            returned = builtin_if(*args)
            assert value == returned
        except AssertionError, e:
            sys.stderr.write("squeamish: test failed: %s led to %s\n" % (
                `i`, returned))
            raise AssertionError

def _test_builtin_dict():
    assert builtin_dict(_elif, _zero, _else, _one) == {"elif": 0, "else": 1}


# Do some testing.
if __name__ == '__main__':
    _test_lazy_map()
    _test_lazy_reduce()
    _test_sub()
    _test_if()
    _test_builtin_dict()
