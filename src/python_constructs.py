"""This file contains support for various Python constructs.

Constructs such as Python imports are supported at the same level as "def" and
"=".

"""

import sys

from Symbol import Symbol


def get_python_constructs(): 
    """Return a dict containing "construct" -> _evaluate_construct."""
    return {
        "pyimport": _evaluate_pyimport,
        ".": _evaluate_attr,
        ".=": _evaluate_attr,
        ".?": _evaluate_attr,
        "del.": _evaluate_attr
    }

def _evaluate_pyimport(value, environ):
    """(pyimport name)
    
    Import the name module (name is anything that resolves to a string) into
    environ.pythonGlobals (if it hasn't already been imported) so that
    subsequent calls by environ to eval will be able to access it.
    environ.pythonGlobals is used instead of __main__ or __builtins__ for
    compatibility with Jython.  Return the module.
    
    """
    from interpreter import evaluate # Circular dependency.
    if len(value) != 2:
        raise SyntaxError("invalid syntax")
    name = evaluate(value[1], environ)
    if not isinstance(name, type("")):
        raise SyntaxError("'%s' is not a string" % name)
    if not environ.pythonGlobals.has_key(name):
        environ.pythonGlobals[name] = __import__(name)
    return environ.pythonGlobals[name]

def _evaluate_attr(value, environ):
    """(get|set|del|has)attr

    (. obj attribute)           # getattr
    (.= obj attribute value)    # setattr
    (.? obj attribute)          # hasattr
    (del. obj attribute)        # delattr

    attribute - This is a Symbol.
    
    """
    from interpreter import evaluate # Circular dependency.
    function = value[0].name
    assert function in [".", ".=", ".?", "del."]
    if function == ".=":
        required_args = 4
        rval = evaluate(value[3], environ)
    else:
        required_args = 3
    if len(value) != required_args:
        raise SyntaxError("invalid syntax")
    obj, attribute = value[1], value[2]
    obj = evaluate(obj, environ)
    if not isinstance(attribute, Symbol):
        raise SyntaxError("attributes must be Symbol's")
    attribute = attribute.name
    if function == ".":
        return getattr(obj, attribute)
    if function == ".=":
        setattr(obj, attribute, rval)
        return rval
    if function == ".?":
        return hasattr(obj, attribute)
    if function == "del.":
        delattr(obj, attribute)


# The following is for testing:
def _test_evaluate_pyimport():
    from Environ import Environ # Circular dependency.
    from interpreter import evaluate # Circular dependency.
    pyimport = Symbol(name = "pyimport")
    locals = Environ()
    assert evaluate([pyimport, "sys"], locals) == sys
    assert locals.pythonGlobals["sys"] == sys
    assert locals.has_key("sys.version")
    
def _test_evaluate_attr():
    from Environ import Environ # Circular dependency.
    from interpreter import evaluate # Circular dependency.
    locals = Environ()
    pyimport = Symbol(name = "pyimport")
    dot = Symbol(name = ".")
    dotEquals = Symbol(name = ".=")
    dotQuestion = Symbol(name = ".?")
    delDot = Symbol(name = "del.")
    UserList = Symbol(name = "UserList")
    foo = Symbol(name = "foo")
    evaluate([pyimport, "UserList"], locals)
    assert not evaluate([dotQuestion, UserList, foo], locals)
    evaluate([dotEquals, UserList, foo, 1], locals)
    assert evaluate([dot, UserList, foo], locals) == 1
    assert evaluate([dotQuestion, UserList, foo], locals)
    evaluate([delDot, UserList, foo], locals)
    assert not evaluate([dotQuestion, UserList, foo], locals)
 

# Do some testing.
if __name__ == '__main__':
    _test_evaluate_pyimport()
    _test_evaluate_attr()
