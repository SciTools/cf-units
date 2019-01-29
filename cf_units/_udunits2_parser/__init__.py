# (C) British Crown Copyright 2019, Met Office
#
# This file is part of cf-units.
#
# cf-units is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cf-units is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cf-units.  If not, see <http://www.gnu.org/licenses/>.

import unicodedata

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from .parser.udunits2Lexer import udunits2Lexer
from .parser.udunits2Parser import udunits2Parser
from .parser.udunits2ParserVisitor import udunits2ParserVisitor
from . import graph


# Dictionary mapping token rule id to token name.
TOKEN_ID_NAMES = {getattr(udunits2Lexer, rule, None): rule
                  for rule in udunits2Lexer.ruleNames}


def handle_UNICODE_EXPONENT(string):
    # Convert unicode to compatibility form, replacing unicode minus with
    # ascii minus (which is actually a less good version
    # of unicode minus).
    normd = unicodedata.normalize('NFKC', string).replace('−', '-')
    return int(normd)


class UnitParseVisitor(udunits2ParserVisitor):
    """
    A visitor which converts the parse tree into an abstract expression graph.

    """
    #: A dictionary mapping lexer TOKEN names to the action that should be
    #: taken on them when visited. For full context of what is allowed, see
    #: visitTerminal.
    TERM_HANDLERS = {
            'CLOSE_PAREN': None,
            'DATE': str,
            'DIVIDE': graph.Operand('/'),  # Drop context, such as " per ".
            'E_POWER': str,
            'FLOAT': graph.Number,  # Preserve precision as str.
            'HOUR_MINUTE_SECOND': str,
            'HOUR_MINUTE': str,
            'ID': graph.Identifier,
            'INT': lambda c: graph.Number(int(c)),
            'MULTIPLY': graph.Operand('*'),
            'OPEN_PAREN': None,
            'PERIOD': str,
            'RAISE': graph.Operand,
            'TIMESTAMP': graph.Timestamp,
            'SIGNED_INT': lambda c: graph.Number(int(c)),
            'SHIFT_OP': None,
            'WS': None,
            'UNICODE_EXPONENT': handle_UNICODE_EXPONENT,
    }

    def defaultResult(self):
        # Called once per ``visitChildren`` call.
        return []

    def aggregateResult(self, aggregate, nextResult):
        # Always result a list from visitChildren
        # (default behaviour is to return the last element).
        if nextResult is not None:
            aggregate.append(nextResult)
        return aggregate

    def visitChildren(self, node):
        # If there is only a single item in the visitChildren's list,
        # return the item. The list itself has no semantics.
        result = super().visitChildren(node)
        while isinstance(result, list) and len(result) == 1:
            result = result[0]
        return result

    def visitTerminal(self, ctx):
        """
        Return a graph.Node, or None, to represent the given lexer terminal.

        """
        content = ctx.getText()

        symbol_idx = ctx.symbol.type
        if symbol_idx == -1:
            # EOF, and all unmatched characters (which will have
            # already raised a SyntaxError).
            result = None
        else:
            name = TOKEN_ID_NAMES[symbol_idx]
            handler = self.TERM_HANDLERS[name]

            if callable(handler):
                result = handler(content)
            else:
                result = handler

        if result is not None and not isinstance(result, graph.Node):
            result = graph.Terminal(result)
        return result

    def visitProduct(self, ctx):
        # UDUNITS grammar makes no parse distinction for Product
        # types ('/' and '*'), so we have to do the grunt work here.
        nodes = self.visitChildren(ctx)

        op_type = graph.Multiply

        if isinstance(nodes, list):
            last = nodes[-1]

            # Walk the nodes backwards applying the appropriate binary
            # operation to each node successively.
            # e.g. 1*2/3*4*5 = 1*(2/(3*(4*5)))
            for node in nodes[:-1][::-1]:
                if isinstance(node, graph.Operand):
                    if node.content == '/':
                        op_type = graph.Divide
                    else:
                        op_type = graph.Multiply
                else:
                    last = op_type(node, last)
            node = last
        else:
            node = nodes
        return node

    def visitTimestamp(self, ctx):
        # For now, we simply amalgamate timestamps into a single Terminal.
        # More work is needed to turn this into a good date/time/timezone
        # representation.
        return graph.Terminal(ctx.getText())

    def visitPower(self, ctx):
        node = self.visitChildren(ctx)
        if isinstance(node, list):
            if len(node) == 3:
                # node[1] is the operator, so ignore it.
                node = graph.Raise(node[0], node[2])
            else:
                node = graph.Raise(*node)
        return node

    def visitShift_spec(self, ctx):
        nodes = self.visitChildren(ctx)
        if isinstance(nodes, list):
            nodes = graph.Shift(*nodes)
        return nodes

    def visitUnit_spec(self, ctx):
        node = self.visitChildren(ctx)
        if not node:
            node = graph.Terminal('')
        return node


class SyntaxErrorRaiser(ErrorListener):
    """
    Turn any parse errors into sensible SyntaxErrors.

    """
    def __init__(self, unit_string):
        self.unit_string = unit_string
        super(ErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # https://stackoverflow.com/a/36367357/741316
        context = ("inline", line, column+2, "'{}'".format(self.unit_string))
        syntax_error = SyntaxError(msg, context)
        raise syntax_error from None


def _debug_tokens(unit_string):
    """
    A really handy way of printing the tokens produced for a given input.

    """
    unit_str = unit_string.strip()
    lexer = udunits2Lexer(InputStream(unit_str))
    stream = CommonTokenStream(lexer)
    parser = udunits2Parser(stream)

    # Actually do the parsing so that we can go through the identified tokens.
    parser.unit_spec()

    for token in stream.tokens:
        if token.text == '<EOF>':
            continue
        token_type_idx = token.type
        rule = TOKEN_ID_NAMES[token_type_idx]
        print("%s: %s" % (token.text, rule))


def normalize(unit_string):
    """
    Parse the given unit string, and return its string representation.

    No standardisation of units, nor simplification of expressions is done,
    but some tokens and operators will be converted to their canonical form.

    """
    return str(parse(unit_string))


def parse(unit_str):
    # The udunits2 definition (C code) says to strip the unit string
    # first.
    unit_str = unit_str.strip()
    lexer = udunits2Lexer(InputStream(unit_str))
    stream = CommonTokenStream(lexer)
    parser = udunits2Parser(stream)

    # Raise a SyntaxError if we encounter an issue when parsing.
    parser.removeErrorListeners()
    parser.addErrorListener(SyntaxErrorRaiser(unit_str))

    # Get the top level concept.
    tree = parser.unit_spec()

    visitor = UnitParseVisitor()
    # Return the graph representation.
    return visitor.visit(tree)
