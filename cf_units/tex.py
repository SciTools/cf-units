# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

import cf_units._udunits2_parser.graph as graph  # noqa: E402
from cf_units._udunits2_parser import parse as _parse  # noqa: E402


class TeXVisitor(graph.Visitor):
    def _format(self, fmt, lhs, rhs):
        return fmt.format(self.visit(lhs), self.visit(rhs))

    def visit_Identifier(self, node):
        token = str(node)
        if token.startswith("micro"):
            token = token.replace("micro", r"{\mu}")
        return token

    def visit_Raise(self, node):
        return self._format("{{{}}}^{{{}}}", node.lhs, node.rhs)

    def visit_Multiply(self, node):
        return self._format(r"{{{}}}\cdot{{{}}}", node.lhs, node.rhs)

    def visit_Divide(self, node):
        return self._format(r"\frac{{{}}}{{{}}}", node.lhs, node.rhs)

    def visit_Shift(self, node):
        return self._format("{{{}}} @ {{{}}}", node.unit, node.shift_from)

    def generic_visit(self, node):
        result = [self.visit(child) for child in node.children()]
        if not result:
            result = str(node)
        return result


def tex(unit_str):
    tree = _parse(unit_str)
    return TeXVisitor().visit(tree)
