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


class Node:
    """
    Represents a node in an expression graph.

    """
    def __init__(self, **kwargs):
        self._attrs = kwargs

    def children(self):
        """
        Return the children of this node.

        """
        # Since this is py>=36, the order of the attributes is well defined.
        return list(self._attrs.values())

    def __getattr__(self, name):
        # Allow the dictionary to raise KeyError if the key doesn't exist.
        return self._attrs[name]

    def _repr_ctx(self):
        # Return a dictionary that is useful for passing to string.format.
        kwargs = ', '.join(
            '{}={!r}'.format(key, value)
            for key, value in self._attrs.items())
        return dict(cls_name=self.__class__.__name__, kwargs=kwargs)

    def __repr__(self):
        return '{cls_name}({kwargs})'.format(**self._repr_ctx())


class Terminal(Node):
    """
    A generic terminal node in an expression graph.

    """
    def __init__(self, content):
        super().__init__(content=content)

    def children(self):
        return []

    def __str__(self):
        return '{}'.format(self.content)


class Operand(Terminal):
    pass


class Number(Terminal):
    pass


class Identifier(Terminal):
    """The unit itself (e.g. meters, m, km and π)"""
    pass


class BinaryOp(Node):
    def __init__(self, lhs, rhs):
        super().__init__(lhs=lhs, rhs=rhs)


class Raise(BinaryOp):
    def __str__(self):
        return f'{self.lhs}^{self.rhs}'


class Multiply(BinaryOp):
    def __str__(self):
        return f'{self.lhs}·{self.rhs}'


class Divide(BinaryOp):
    def __str__(self):
        return f'{self.lhs}/{self.rhs}'


class Shift(Node):
    def __init__(self, unit, shift_from):
        # The product unit to be shifted.
        super().__init__(unit=unit, shift_from=shift_from)

    def __str__(self):
        return f'({self.unit} @ {self.shift_from})'


class Timestamp(Terminal):
    # Currently we do not try to interpret the timestamp.
    # This is likely to change in the future, but there are some
    # gnarly test cases, and should not be undertaken lightly.
    pass


class Visitor:
    """
    This class may be used to help traversing an expression graph.

    It follows the same pattern as the Python ``ast.NodeVisitor``.
    Users should typically not need to override either ``visit`` or
    ``generic_visit``, and should instead implement ``visit_<ClassName>``.

    This class is used in cf_units.latex to generate a latex representation
    of an expression graph.

    """
    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """
        Called if no explicit visitor function exists for a node.

        Can also be called by ``visit_<ClassName>`` implementations
        if children of the node are to be processed.

        """
        return [self.visit(child) for child in node.children()]
