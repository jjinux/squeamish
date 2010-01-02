"""This file contains the Symbol class."""

from AutomaticClass import AutomaticClass


class Symbol(AutomaticClass):

    """This class represents a symbol in the parse tree.
    
    The following attributes are used:

    name - This is the name of the symbol.

    """

    def getAttributes(self):
        return AutomaticClass.getAttributes(self) + ["name"]

    def __eq__(self, other):
        """Two symbols are equal if they have the same name."""
        return self.name == other.name

    def __ne__(self, other):
        """Two symbols are not equal if they have different names."""
        return self.name != other.name

    def __hash__(self):
        return hash(`self`)


# Do some testing.
if __name__ == '__main__':
    assert Symbol(name = "+") == Symbol(name = "+")
    assert Symbol(name = "+") != Symbol(name = "-")
    assert not (Symbol(name = "+") != Symbol(name = "+"))
    assert hash(Symbol(name = "+")) == hash(Symbol(name = "+"))
