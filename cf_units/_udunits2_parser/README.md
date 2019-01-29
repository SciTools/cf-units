# cf-units parser of UDUNITS-2 grammar

This sub-package is an attempt to re-implement the
[UDUNITS-2 grammar](https://www.unidata.ucar.edu/software/udunits/udunits-2.0.4/udunits2lib.html#Grammar)
in an implementation agnostic manner, using the power of ANTLRv4.

The [lexer](udunits2Lexer.g4.jinja) is a Jinja2 template which expands
the multi-mode tokenizer of the UDUNITS-2 grammar.
The [parser](udunits2Parser.g4) defines the grammar of the tokens, along with
a number of convenient lexical elements.


### Generating the parser from the grammar

Once the Jinja2 template has been expanded, the
[ANTLR Java library](https://github.com/antlr/antlr4) is used to
compile the grammar into the targetted runtime language.

[A script](compile.py) is provided to automate this as much as possible.

The compiled parser is committed to the repository for ease of
deployment and testing (we know it isn't ideal, but it really does make things easier).
Please commit the changed parser at the same time as any
changes to the grammar being proposed so that the two can remain in synch.


### Testing the gammar

An extensive set of tests exist to confirm that the parser produces equivalent results
to the UDUNITS-2 reference implementation.
The usual ``pytest cf_units`` includes these tests by default.
They are typically very fast to execute, but significant slowdowns were experienced
(x15 slowdown) when left-recursive rules were not carefully implemented, therefore please
be conscious of performance when modifying the grammar.
