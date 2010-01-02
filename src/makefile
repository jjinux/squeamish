# Permit the user to switch to Jython, etc.
PYTHON?=	python

# There's not really anything to build.
all:

# Clean everything, including the PLY generated stuff.
clean:
		rm -f *.pyc *.pyo *.class parser.out parsetab.py ../test/out

# Run internal and external regression tests.
test: test_internal test_external

# Some of the files accept standard input in order to do manual tests after
# running internal tests.  Hence, use echo -n to feed them nothing.
test_internal:
	@for i in *.py; do \
		echo -n | ${PYTHON} "$$i" > /dev/null; \
	done

# Run each external test and compare its output to the corresponding output 
# file.
test_external:
	@for i in ../test/*.sqm; do \
		./squeamish "$$i" > ../test/out; \
		diff `echo "$$i" | sed 's/.sqm$$/.out/g'` ../test/out || \
		(echo "test_external: Failed test: $$i"; exit 1); \
	done

# Return a list of Python files that I wrote; specifically, do not include
# lex.py and yacc.py.
listmine:
	@find . -name '*.py' -a ! -name 'lex.py' -a ! -name 'yacc.py'
