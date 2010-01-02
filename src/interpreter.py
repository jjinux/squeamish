"""This file contains the interpreter."""

import sys

from parser import yacc
from python_constructs import get_python_constructs
from Symbol import Symbol
from function import create_function
from external_function import create_external_function


def evaluate(value, environ):
    """Evaluate value in the given environ.
    
    Return the following:

    Given an int, float, string, or something callable, just return it.
    Given a symbol, do a lookup, and return the result.
    Given a list:
        Given an empty list, return None.
        Given a supported construct, call the associated handler.
        Otherwise, treat the list as a function call.  Return the value of
            _evaluate_call.
    Otherwise, raise a SyntaxError.

    """
    if (isinstance(value, type(0)) or 
        isinstance(value, type(0.0)) or
        isinstance(value, type("")) or
        callable(value)):
        return value
    if isinstance(value, Symbol):
        return environ[value.name]
    if isinstance(value, type([])):
        if value == []:
            return None
        if isinstance(value[0], Symbol):
            name = value[0].name
            if constructs.has_key(name):
                return constructs[name](value, environ)
        return _evaluate_call(value, environ)
    raise SyntaxError("invalid syntax")

def _evaluate_assignment(value, environ):
    """(= a b)
    
    Set a to b and return b.  b will be evaluated--assignment is not lazy.
    
    """
    if len(value) != 3: 
        raise SyntaxError("invalid syntax")
    if not isinstance(value[1], Symbol):
        raise SyntaxError("can't assign to non-symbol")
    lval, rval = value[1], evaluate(value[2], environ)
    environ[lval.name] = rval
    return rval

def _evaluate_def(value, environ):
    """(def name(parameters...) statements...)

    Create a user-defined function and insert it into environ with the given
    name (unless name is "_", which is used for anonymous functions).   Return
    the function.

    """
    if len(value) < 4:
        raise SyntaxError("invalid syntax")
    if not isinstance(value[1], Symbol):
        raise SyntaxError("invalid syntax")
    if not isinstance(value[2], type([])):
        raise SyntaxError("invalid syntax")
    name, statements = value[1].name, value[3:]
    parameters = []
    for i in value[2]:
        if not isinstance(i, Symbol):
            raise SyntaxError("invalid syntax")
        parameters.append(i.name)
    f = create_function(name, parameters, statements)
    if name != "_":
        environ[name] = f
    return f

def _evaluate_del(value, environ):
    """(del a)

    Call environ.del_local(a).  Return None.

    """
    if len(value) != 2:
        raise SyntaxError("invalid syntax")
    if not isinstance(value[1], Symbol):
        raise SyntaxError("can't del a non-symbol")
    key = value[1].name
    environ.del_local(key)
    return None

def _evaluate_call(value, environ):
    """(function arguments...)
    
    Evaluate function to reduce it to something that is callable.  Then, apply
    the function to the given arguments, if any, and return the result.  If 
    the function does not have an attribute named lazy, it needs to be wrapped
    using create_external_function before being called.

    """
    if len(value) < 1:
        raise SyntaxError("invalid syntax")
    name, f, args = value[0], evaluate(value[0], environ), value[1:]
    if not callable(f) and type(f).__name__ != "org.python.core.PyJavaClass":
        raise TypeError("'%s' is not callable" % `name`)
    if not hasattr(f, "lazy"):
        f = create_external_function(f.__name__, f)
    return f(environ, *args)

# This is a dict containing a mapping from each construct (such as "=") to a 
# handler for that construct (such as "_evaluate_def").
constructs = {
    "=": _evaluate_assignment,
    "def": _evaluate_def,
    "del": _evaluate_del,
}
constructs.update(get_python_constructs())


# The following is for testing:
def _test_evaluate_assignment():
    from Environ import Environ # Circular dependency.
    foo = Symbol(name = "foo")
    equals = Symbol(name = "=")
    locals = Environ()
    assert evaluate([equals, foo, "bar"], locals) == "bar"
    assert locals["foo"] == "bar"

def _test_evaluate_def():
    from Environ import Environ # Circular dependency.
    locals = Environ()
    def_ = Symbol(name = "def")
    foo = Symbol(name = "foo")
    bar = Symbol(name = "bar")
    _ = Symbol(name = "_")
    f = evaluate([def_, foo, [bar], []], locals)
    assert callable(locals["foo"])
    assert hasattr(locals["foo"], "lazy")
    evaluate([def_, _, [bar], 1], locals)
    assert not locals.has_key(_.name)

def _test_evaluate_del():
    from Environ import Environ # Circular dependency.
    foo = Symbol(name = "foo")
    equals = Symbol(name = "=")
    del_ = Symbol(name = "del")
    locals = Environ()
    assert evaluate([equals, foo, "bar"], locals) == "bar"
    assert locals["foo"] == "bar"
    assert evaluate([del_, foo], locals) == None
    assert not locals.has_key("foo")

def _internal_tests():
    from Environ import Environ # Circular dependency.
    plus = Symbol(name = "+")
    tests = [
        ("()", None),
        ("(' 1 2)", [1, 2]),
        ("(+ 1 2)", 3),
        ("(+ (+ 1 2) 3)", 6),
        ("(+ 1(+ 2 3))", 6),
        ('(+ "foo" "bar")', "foobar")
    ]
    for i in tests:
        (s, value) = i
        try:
            returned = evaluate(yacc.parse(s), Environ())
            assert value == returned
        except AssertionError, e:
            sys.stderr.write("squeamish: test failed: %s led to %s\n" % (
                `i`, returned))
            raise AssertionError

def _external_tests():
    from Environ import Environ # Circular dependency.
    environ = Environ()
    while 1:
        try:
            s = raw_input("squeamish> ")
        except EOFError:
            break
        if not s:
            continue
        print evaluate(yacc.parse(s), environ)


# Do some testing.
if __name__ == '__main__':
    _test_evaluate_assignment()
    _test_evaluate_def()
    _test_evaluate_del()
    _internal_tests()
    _external_tests()
