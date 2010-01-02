"""This file contains the Shell class."""

import sys
from traceback import print_exception

from parser import yacc
from Environ import Environ
from interpreter import evaluate


class Shell:

    """Handle command-line arguments and call the interpreter.

    This class reads input from either STDIN or an input file specified on the
    command line.  It then passes off complete "statements" to the interpreter.
    It does just a little parsing to recognize multi-line statements which must
    be passed together.

    The following attributes are used: 

    input - This is the file handle where input is read from.
    isStdin - Is self.input == sys.stdin?
    environ - This is the global Environ.

    """

    def __init__(self):
        """Do basic initialization."""
        argvlen = len(sys.argv)
        if argvlen > 2:
            sys.stderr.write("usage: squeamish [file]\n")
            sys.exit(1)
        if argvlen == 2:
            self.input = open(sys.argv[1], "r")
        else:
            self.input = sys.stdin
        self.isStdin = self.input == sys.stdin
        self.environ = Environ()

    def mainLoop(self):
        """This is the main loop."""
        while 1:
            try:
                line = ""
                while not self.isComplete(line):
                    line += self.readline(line)
                value = evaluate(yacc.parse(line), self.environ)
                if self.isStdin and value:
                    print value
            except EOFError:
                self.input.close()
                break
            except:
                print_exception(*(sys.exc_info()))

    def readline(self, continuation = 0):
        """Read a line from self.input.
        
        continuation - Is this line a continuation of an earlier statement?

        The line will contain the trailing newline.  If no more input is 
        available, EOFError will be raised.
        
        """
        if not self.isStdin:
            line = self.input.readline()
            if not line: 
                raise EOFError
            return line
        else:
            if continuation:
                prompt = "... "
            else:
                prompt = "squeamish> "
            try: 
                return raw_input(prompt) + "\n"
            except ValueError: # User hit ^D.
                raise EOFError

    def isComplete(self, line):
        """Is the given line a complete statement?"""
        inQuotes = 0
        escaped = 0
        parenStack = 0
        sawParen = 0
        for c in line:
            if inQuotes:
                if escaped:
                    escaped = 0
                else:
                    if c == '"':
                        inQuotes = 0
                    if c == "\\":
                        escaped = 1
            else:
                if c == '"':
                    inQuotes = 1
                elif c == "(":
                    parenStack += 1
                    sawParen = 1
                elif c == ")":
                    parenStack -= 1
                    if parenStack < 0:
                        raise SyntaxError("too many closing parenthesis")
        return parenStack == 0 and sawParen


# Do some testing.
if __name__ == '__main__':
    Shell().mainLoop()
