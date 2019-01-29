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

import six

if six.PY2:
    raise ImportError('Python3 required for cf-units latex support')

import cf_units._udunits2_parser.graph as graph  # noqa: E402
from cf_units._udunits2_parser import parse as _parse  # noqa: E402


class TeXVisitor(graph.Visitor):
    def _format(self, fmt, lhs, rhs):
        return fmt.format(self.visit(lhs), self.visit(rhs))

    def visit_Identifier(self, node):
        token = str(node)
        if token.startswith('micro'):
            token = token.replace('micro', '{\mu}')
        return token

    def visit_Raise(self, node):
        return self._format('{{{}}}^{{{}}}', node.lhs, node.rhs)

    def visit_Multiply(self, node):
        return self._format(r'{{{}}}\cdot{{{}}}', node.lhs, node.rhs)

    def visit_Divide(self, node):
        return self._format(r'\frac{{{}}}{{{}}}', node.lhs, node.rhs)

    def visit_Shift(self, node):
        return self._format('{{{}}} @ {{{}}}', node.unit, node.shift_from)

    def generic_visit(self, node):
        result = [self.visit(child) for child in node.children()]
        if not result:
            result = str(node)
        return result


def tex(unit_str):
    tree = _parse(unit_str)
    return TeXVisitor().visit(tree)
