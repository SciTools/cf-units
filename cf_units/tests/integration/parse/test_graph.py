# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

import cf_units._udunits2_parser.graph as g
from cf_units._udunits2_parser import parse


def test_Node_attributes():
    n = g.Node(a=1, kwarg="two", arbitrary_kwargs=3)

    assert n.a == 1
    assert n.kwarg == "two"
    assert n.arbitrary_kwargs == 3


def test_Node_str():
    n = g.Node(a=1, kwarg="two", arbitrary_kwargs=3)
    assert str(n) == "Node(a=1, kwarg='two', arbitrary_kwargs=3)"


def test_Node_children():
    n = g.Node(a=1, kwarg="two", arbitrary_kwargs=3)
    # Ordered, and consistent.
    assert n.children() == [1, "two", 3]


def test_large_graph():
    graph = parse("m2/4.1.2π per second @ 10")
    assert isinstance(graph, g.Shift)

    unit, shift_from = graph.children()
    assert isinstance(shift_from, g.Number)
    assert str(shift_from) == "10"

    assert isinstance(unit, g.Divide)
    lhs, rhs = unit.children()
    assert str(lhs) == "m^2/4.1·.2·π"
    assert str(rhs) == "second"

    assert isinstance(lhs, g.Multiply)
    lhs, rhs = lhs.children()
    assert str(lhs) == "m^2/4.1·.2"
    assert str(rhs) == "π"

    assert isinstance(lhs, g.Multiply)
    lhs, rhs = lhs.children()
    assert str(lhs) == "m^2/4.1"
    assert str(rhs) == ".2"

    assert isinstance(lhs, g.Divide)
    lhs, rhs = lhs.children()
    assert str(lhs) == "m^2"
    assert str(rhs) == "4.1"

    assert isinstance(lhs, g.Raise)
    lhs, rhs = lhs.children()
    assert str(lhs) == "m"
    assert str(rhs) == "2"
