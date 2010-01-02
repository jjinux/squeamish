"""This file contains the Environ class."""

from UserDict import UserDict
import re

from Expression import Expression
from builtin_function import create_builtin_function
from builtins import builtins


class Environ(UserDict):

    """This is the environment (i.e. symbol table).

    This class is just a dict with a few additions:

    1) It implicitly supports nesting in order to implement nested scopes.
       This is based on the chain of responsibility design pattern.

    2) While looking for a key, if the key isn't found in any of the parents,
       the Python environment is searched next.  

    3) In order to implement lazy evaluation of function parameters for 
       user-defined functions (see also Parameter.py), the value associated
       with a function parameter will be an Expression instance.  When a lookup
       is done on the function parameter, the Expression will be evaluated
       (using the Expression's Environ--the context of a parameter is not the
       same as that of an argument).  This new value will be cached (to insure
       evaluation only happens once, in case there are side effects) and
       returned.

    The keys used in this dict are strings (there's no need to 
    encapsulate the strings in Symbol instances since there can be no 
    confusion been a normal string and a Symbol, like in a parse tree).  The
    values will be normal values such as ints, floats, user-defined functions,
    etc.
    
    The following attributes are used:

    parent - This is the parent Environ.  

    pythonGlobals - This will be passed to eval anytime it is used.  Sometimes
    it is necessary to put stuff in the global Python namespace, which is 
    challenging in Jython.  There is only one copy of this dict per nested
    Environ hierarchy.

    """

    def __init__(self, parent = builtins, *args, **kargs):
        """Extend the base class constructor to accept parent.
        
        parent - By default, parent is set to a new Environ containing the 
        builtins (which will be properly wrapped using 
        create_builtin_function).  If you do not wish to have a parent, pass
        None.  Otherwise, pass an existing parent.

        args, kargs - These are passed to UserDict.__init__.
        
        """
        UserDict.__init__(self, *args, **kargs)
        if parent == builtins:
            parent = Environ(parent = None)
            for (key, val) in builtins.items():
                if callable(val):
                    val = create_builtin_function(key, val)
                parent[key] = val
        self.parent = parent
        if self.parent:
            self.pythonGlobals = self.parent.pythonGlobals
        else:
            self.pythonGlobals = {}

    def __getitem__(self, s):
        """Look up the value of a string.

        o The lookup order is self, self.parent, Python.
        o If the value is an Expression, evaluate it (in its own Environ), 
          cache the value, and return it.  
        o Searches into the Python namespace will only be done for valid
          identifiers.  self.pythonGlobals will be passed to eval.
        o Complete failures will result in a NameError.
        
        """
        from interpreter import evaluate # Circular dependency.
        if self.data.has_key(s):
            val = self.data[s]
            if isinstance(val, Expression):
                val = evaluate(val.parseTree, val.environ)
                self.data[s] = val
            return val
        if self.parent != None: # For some reason, "!= None" is necessary.
            return self.parent[s]
        if re.match(r'^[\w\.]+$', s):
            return eval(s, self.pythonGlobals)
        raise NameError("name '%s' is not defined" % s)

    def has_key(self, key):
        """Do we have the given key?"""
        try:
            self[key]
            return 1
        except NameError:
            return 0

    def del_local(self, key):
        """Delete key from self.

        If there is no such key in this Environ, do not recurse to parent
        Environ's.  Instead, raise a NameError.

        """
        if self.data.has_key(key):
            del self.data[key]
        else:
            raise NameError("name '%s' is not defined" % key)


# Do some testing.
if __name__ == '__main__':
    globals = Environ(parent = None)
    assert not globals.has_key("+")
    assert globals.has_key("int")
    globals = Environ()
    assert globals.pythonGlobals == globals.parent.pythonGlobals
    assert globals.has_key("+")
    globals["foo"] = "bar"
    locals = Environ(globals)
    assert locals.has_key("foo")
    assert locals["foo"] == "bar"
    locals["foo"] = "spam"
    assert locals["foo"] == "spam"
    assert globals["foo"] == "bar"
    locals.del_local("foo")
    assert globals["foo"] == "bar"
