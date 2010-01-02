"""This file contains the Parameter class."""

from AutomaticClass import AutomaticClass

from Expression import Expression
from Symbol import Symbol


class Parameter(AutomaticClass):

    """This encapsulates a parameter to a builtin function.

    In order to implement lazy evaluation of function parameters for 
    builtin functions (see also Environ.py and builtins.py), the value
    associated with a function parameter will be an Expression instance.  When
    a lookup is done on the function parameter, the Expression will be
    evaluated.  This new value will be cached (to insure evaluation only
    happens once, in case there are side effects) and returned.
    
    The following attributes are used:

    value - This is initially an Expression.  See __call__.
    
    """

    def getAttributes(self):
        return AutomaticClass.getAttributes(self) + ["value"]

    def __call__(self, implicitUnval=0, implicitLast=0):
        """Do lazy evaluation.
        
        Return value after having evaluated it.  Cache the evaluation so that
        subsequent calls don't cause additional evaluations (in case there
        are side effects).
        
        implicitUnval - During evaluation, if the Expression.parseTree is a 
        list, automatically treat the list as data (i.e. a call to the unval
        function) instead of a normal function call.  This is required in 
        certain situations such as the value (i.e. body) of an if statement,
        which are meant to feel like the body of a function definition.

        implicitLast - If after evaluation, the value is a list, return only
        the last element of that list.  Like implicitUnval, this is required in
        certain situations such as the value (i.e. body) of an if statement,
        which are meant to feel like the body of a function definition.

        """
        from interpreter import evaluate # Circular dependency.
        if isinstance(self.value, Expression):
            parseTree = self.value.parseTree
            if implicitUnval and isinstance(parseTree, type([])):
                parseTree.insert(0, Symbol(name = "'"))
            val = evaluate(parseTree, self.value.environ)
            if implicitLast and isinstance(val, type([])):
                val = val[-1]
            self.value = val
        return self.value


# Do some testing.
if __name__ == '__main__':
    from Environ import Environ # Circular dependency.
    environ = Environ()
    p = Parameter(value = Expression(environ = environ, parseTree = "foo")) 
    assert p() == p()
    assert p() == "foo"
    p = Parameter(value = Expression(environ = environ, parseTree = [1, 2]))
    assert p(implicitUnval = 1) == [1, 2]
    p = Parameter(
        value = Expression(environ = environ, 
            parseTree = [Symbol(name = "'"), 1, 2]))
    assert p(implicitLast = 1) == 2
    p = Parameter(
        value = Expression(environ = environ, 
            parseTree = [1, 2]))
    assert p(implicitUnval = 1, implicitLast = 1) == 2
