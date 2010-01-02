"""This file contains the Expression class."""

from AutomaticClass import AutomaticClass


class Expression(AutomaticClass):
    
    """This encapsulates a non-evaluated value (e.g. a function call).
    
    The following attributes are used:

    environ - This is the Environ in which to evaluate the expression.  
    Naturally, an expression must be considered within its context.
    
    parseTree - This is the expression.

    """

    def getAttributes(self):
        return AutomaticClass.getAttributes(self) + ["environ", "parseTree"]


# Do some testing.
if __name__ == '__main__':
    Expression(environ = None, parseTree = [])
