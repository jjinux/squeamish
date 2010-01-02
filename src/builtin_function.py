"""This file contains the create_builtin_function function."""

from __future__ import nested_scopes 

from Symbol import Symbol
from Expression import Expression
from Parameter import Parameter


def create_builtin_function(name, function):
    
    """Return a builtin function.

    This function creates a closure for the returned function.  The returned 
    function will have the "lazy" attribute set to 1.

    name - This is a string.

    function - This is the actual Python function.

    """

    def closure(environ, *args):
        """Apply the function to args, and return the results.

        Wrap each argument in a Parameter instance before applying the 
        function.  Please see Parameter.py and builtins.py.

        """
        parameters = []
        for i in args:
            expression = Expression(environ = environ, parseTree = i)
            parameter = Parameter(value = expression)
            parameters.append(parameter)
        return function(*parameters)

    closure.lazy = 1
    return closure


# Do some testing.
if __name__ == '__main__':
    from Environ import Environ # Circular dependency.
    from interpreter import evaluate # Circular dependency.
    locals = Environ()
    def builtin_add(a, b): return a() + b()
    locals["+"] = create_builtin_function("+", builtin_add)
    assert hasattr(locals["+"], "lazy")
    plus = Symbol(name = "+")
    assert evaluate([plus, 1, [plus, 1, 1]], locals) == 3
