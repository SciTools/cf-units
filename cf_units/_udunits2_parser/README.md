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
compile the grammar into the targeted runtime language.

[A script](compile.py) is provided to automate this as much as possible.
It has a dependency on pip, Jinja2, Java and ruff.

The compiled parser is committed to the repository for ease of
deployment and testing (we know it isn't ideal, but it really does make things easier).
Please commit the changed parser at the same time as any
changes to the grammar being proposed so that the two can remain in synch.

### Updating the ANTLR version

The [compile.py script](compile.py) copies the ANTLR4 runtime into the _antlr4_runtime
directory, and this should be commited to the repository. This means that we do not
have a runtime dependency on ANTLR4 (which was found to be challenging due to the
fact that you need to pin to a specific version of the ANTLR4 runtime, and aligning
this version with other libraries which also have an ANTLR4 dependency is impractical).

Since the generated code is committed to this repo, and the ANTRL4 runtime is also vendored into it, we won't ever need to run ANTLR4 unless the grammar changes.

So, we will  only change the ANTLR4 version if we need new features of the
parser/lexer generators, or it becomes difficult to support the older version.

Upgrading the version is a simple matter of changing the version in the compile.py
script, and then re-running it. This should re-generate the parser/lexer, and update
the content in the _antlr4_runtime directory. One complexity may be that the imports
of the ANTRL4 runtime need to be rewritten to support vendoring, and the code needed
to do so may change from version to version. This topic is being followed upstream
with the ANTRL4 project with the hope of making this easier and/or built-in to ANTLR4.

### Testing the grammar

An extensive set of tests exist to confirm that the parser produces equivalent results
to the UDUNITS-2 reference implementation.
The usual ``pytest cf_units`` includes these tests by default.
They are typically very fast to execute, but significant slowdowns were experienced
(x15 slowdown) when left-recursive rules were not carefully implemented, therefore please
be conscious of performance when modifying the grammar.
