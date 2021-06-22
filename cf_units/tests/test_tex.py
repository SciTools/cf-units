# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.

from cf_units.tex import tex


def test_basic():
    u = "kg kg-1"
    assert tex(u) == r"{kg}\cdot{{kg}^{-1}}"


def test_identifier_micro():
    u = "microW m-2"
    assert tex(u) == r"{{\mu}W}\cdot{{m}^{-2}}"


def test_raise():
    u = "m^2"
    assert tex(u) == r"{m}^{2}"


def test_multiply():
    u = "foo bar"
    assert tex(u) == r"{foo}\cdot{bar}"


def test_divide():
    u = "foo per bar"
    assert tex(u) == r"\frac{foo}{bar}"


def test_shift():
    u = "foo @ 50"
    assert tex(u) == r"{foo} @ {50}"


def test_complex():
    u = "microW^2 / (5^-2)π per sec @ 42"
    expected = r"{\frac{{\frac{{{\mu}W}^{2}}{{5}^{-2}}}\cdot{π}}{sec}} @ {42}"
    assert tex(u) == expected
