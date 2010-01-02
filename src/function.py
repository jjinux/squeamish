"""This file contains the create_function function."""

from __future__ import nested_scopes 

from Symbol import Symbol
from Expression import Expression


def create_function(name, parameters, body):

    """Return a user-defined function.
    
    This function creates a closure for the returned function.  The returned 
    function will have the "lazy" attribute set to 1.

    name - This is a string.

    parameters - This is a list of strings.

    body - This is a parse tree.
    
    """

    def closure(environ, *args):
        """Apply the function to args, and return the results.
        
        Note, the function application should take place in a newly nested 
        Environ.  In this newly nested Environ, tie the formal arguments to
        the parameters using Expression's in order to implement lazy
        evaluation.  On the other hand, the parameter Expression's should be
        evaluated in the caller's Environ (i.e. (sum a b) should evaluate a and
        b in the caller's Environ, not sum's Environ).
        
        Return the last executed "statement" of the function.

        """
        from Environ import Environ # Circular dependency.
        from interpreter import evaluate # Circular dependency.
        if not len(parameters) == len(args):
            raise TypeError("%s() takes exactly %d arguments (%d given)" % 
                (name, len(parameters), len(args)))
        locals = Environ(parent = environ)
        for i in range(0, len(parameters)): 
            locals[parameters[i]] = Expression(environ = environ,
                parseTree = args[i])
        for i in body:
            ret = evaluate(i, locals)
        return ret

    closure.lazy = 1
    return closure


# Do some testing.
if __name__ == '__main__':
    from Environ import Environ # Circular dependency.
    from interpreter import evaluate # Circular dependency.
    locals = Environ()
    def_ = Symbol(name = "def")
    foo = Symbol(name = "foo")
    _ = Symbol(name = "_")
    arg1 = Symbol(name = "arg1")
    arg2 = Symbol(name = "arg2")
    div_ = Symbol(name = "/")
    f = evaluate([def_, foo, [arg1, arg2], arg1], locals)
    assert hasattr(f, "lazy")
    assert evaluate([foo, "spam", [div_, 1, 0]], locals) == "spam"
    assert evaluate([f, "spam", [div_, 1, 0]], locals) == "spam"
    assert not locals.has_key(arg1.name)
