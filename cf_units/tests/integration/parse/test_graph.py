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

from cf_units._udunits2_parser import parse
import cf_units._udunits2_parser.graph as g


def test_Node_attributes():
    n = g.Node(a=1, kwarg='two', arbitrary_kwargs=3)

    assert n.a == 1
    assert n.kwarg == 'two'
    assert n.arbitrary_kwargs == 3


def test_Node_str():
    n = g.Node(a=1, kwarg='two', arbitrary_kwargs=3)
    assert str(n) == "Node(a=1, kwarg='two', arbitrary_kwargs=3)"


def test_Node_children():
    n = g.Node(a=1, kwarg='two', arbitrary_kwargs=3)
    # Ordered, and consistent.
    assert n.children() == [1, 'two', 3]


def test_large_graph():
    graph = parse('m2/4.1.2π per second @ 10')
    assert isinstance(graph, g.Shift)

    unit, shift_from = graph.children()
    assert isinstance(shift_from, g.Number)
    assert str(shift_from) == '10'

    assert isinstance(unit, g.Divide)
    lhs, rhs = unit.children()
    assert str(lhs) == 'm^2/4.1·.2·π'
    assert str(rhs) == 'second'

    assert isinstance(lhs, g.Multiply)
    lhs, rhs = lhs.children()
    assert str(lhs) == 'm^2/4.1·.2'
    assert str(rhs) == 'π'

    assert isinstance(lhs, g.Multiply)
    lhs, rhs = lhs.children()
    assert str(lhs) == 'm^2/4.1'
    assert str(rhs) == '.2'

    assert isinstance(lhs, g.Divide)
    lhs, rhs = lhs.children()
    assert str(lhs) == 'm^2'
    assert str(rhs) == '4.1'

    assert isinstance(lhs, g.Raise)
    lhs, rhs = lhs.children()
    assert str(lhs) == 'm'
    assert str(rhs) == '2'
