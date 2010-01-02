"""This file contains the create_external_function function."""

from __future__ import nested_scopes 

from Symbol import Symbol


def create_external_function(name, function):
    
    """Return an external function.

    This function creates a closure for the returned function.

    name - This is a string.

    function - This is the actual Python function.

    """

    def closure(environ, *args):
        """Apply the function to args, and return the results.

        Because Python does not support lazy evaluation, the args must be 
        evaluated before passing them to the function.

        """
        from interpreter import evaluate # Circular dependency.
        parameters = [evaluate(i, environ) for i in args]
        return function(*parameters)

    return closure


# Do some testing.
if __name__ == '__main__':
    from Environ import Environ # Circular dependency.
    from interpreter import evaluate # Circular dependency.
    locals = Environ()
    str_ = Symbol(name = "str")
    assert evaluate([str_, 1], locals) == "1"
    assert not hasattr(locals["str"], "lazy")
