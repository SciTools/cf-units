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

import re

import pytest

import cf_units
from cf_units._udunits2_parser import normalize


testdata = [
    '',
    '1',
    '12',
    '1.2',
    '+1',
    '+1.2',
    '-1',
    '-1.2',
    '-1.2e0',
    '2e6',
    '2e-6',
    '2.e-6',
    '.1e2',
    '.1e2.2',
    '2e',  # <- TODO: Assert this isn't 2e1, but is infact the unit e *2
    'm',
    'meter',

    # Multiplication
    '1 2 3',
    '1 -2 -3',
    '1m',
    '1*m',
    'm·m',
    '1 m',
    '1   m',
    'm -1',
    'm -1.2',
    'm 1',
    'm 1.2',
    'm-+2',
    'm--4',
    'm*1*2',
    'm--2--3',

    # TODO: add some tests with brackets.
    'm(2.3)',
    'm(2.3m)',
    '(1.2)(2.4)',
    '(5m(6s-1))',
    '2*3*4/5m/6*7*8',


    'm/2',
    'm1',
    'm m',
    'm2',
    'm+2',
    'm¹',
    'm²',
    'm³',
    '2⁴',  # NOTE: Udunits can't do m⁴ for some reason. Bug?
    '2⁵',
    '2⁴²',
    '3⁻²',
    'm2 s2',
    'm^2*s^2',

    '1-2',
    '1-2-3',  # nb. looks a bit like a date, but it isn't!
    'm-1',
    'm^2',
    'm^+2',
    'm^-1',
    'm.2',    # This is 2*m
    'm.+2',   # 2*m
    'm.2.4',  # This is 2.4 * m
    'm0.2',   # But this is 2 m^0
    'm2.5',   # And this is 5m^2
    'm2.3.4',  # 0.4 * m^2
    'm--1',

    # Division
    'm per 2',
    'm per s',
    'm / 2',

    # Shift
    'm@10',
    'm @10',
    'm @ 10',
    'm@ 10',
    'm from2',
    'm from2e-1',
    '(m @ 10) (s @ 10)',

    # Date shift
    's from 1990',
    'minutes since 1990',
    'hour@1990',
    'hours from 1990-1',
    'hours from 1990-1-1',
    'hours from 1990-1-1 0',
    'hours from 1990-1-1 0:1:1',
    'hours from 1990-1-1 0:0:1 +2',
    's since 1990-1-2+5:2:2',
    's since 1990-1-2+5:2',
    's since 1990-1-2 5 6:0',  # Undocumented packed_clock format?
    's since 19900102T5',  # Packed format (undocumented?)
    's since 19900101T190030 +2',
    's since 199022T1',  # UGLY! (bug?).

    's since 1990 +2:0:2.9',
    's since 1990-2T1',
    'hours from 1990-1-1 -19:4:2',
    'hours from 1990-1-1 3+1',

    'seconds from 1990-1-1 0:0:0 +2550',
    's since 1990-1-2+5:2:2',
    'hours from 1990-1-1 0:1:60',
    'hours from 1990-1-1 0:1:62',

    '(hours since 1900) (s since 1980)',  # Really fruity behaviour.

    # Unicode / constants
    'π',
    'e',
    '°C',
]

invalid = [
    '1 * m',
    'm--m',
    '-m',
    '.1e2.',
    'm+-1',
    '--1',
    '+-1',
    '--3.1',
    '$',
    '£',
    'hours from 1990-0-0 0:0:0',
    'hours since 1900-1 10:12 10:0 1',
    's since 1990:01:02T1900 +1',
]


@pytest.mark.parametrize("_, unit_str", enumerate(testdata))
def test_normed_units_equivalent(_, unit_str):
    # nb: The "_" argument makes it easier to see which test was being run.

    # Get the udunits symbolic form for the raw unit.
    raw_symbol = cf_units.Unit(unit_str).symbol

    # Now get the parsed form of the unit, and then convert that to
    # symbolic form. The two should match.
    unit_expr = normalize(unit_str)
    parsed_expr_symbol = cf_units.Unit(unit_expr).symbol

    # Whilst the symbolic form from udunits is ugly, it *is* acurate,
    # so check that the two represent the same unit.
    assert raw_symbol == parsed_expr_symbol


udunits_bugs = [
        '2¹²³⁴⁵⁶⁷⁸⁹⁰',
        'm⁻²'
]


@pytest.mark.parametrize("_, unit_str", enumerate(invalid))
def test_invalid_units(_, unit_str):
    # Confirm that invalid udunits-2 units are also invalid in our grammar.

    try:
        cf_units.Unit(unit_str)
        cf_valid = True
    except ValueError:
        cf_valid = False

    # Double check that udunits2 can't parse this.
    assert cf_valid is False, \
        'Unit {!r} is unexpectedly valid in UDUNITS2'.format(unit_str)

    try:
        normalize(unit_str)
        can_parse = True
    except SyntaxError:
        can_parse = False

    # Now confirm that we couldn't parse this either.
    msg = 'Parser unexpectedly able to deal with {}'.format(unit_str)
    assert can_parse is False, msg


def multi_enumerate(items):
    # Like enumerate, but flattens out the resulting index and items.
    return [[i, *item] for i, item in enumerate(items)]


not_udunits = [
    ['foo', 'foo'],
    ['mfrom1', 'mfrom^1'],
    ['m⁴', 'm^4'],  # udunits bug.
    ['2¹²³⁴⁵⁶⁷⁸⁹⁰', '2^1234567890'],

    # Unicode (subset of the subset).
    ['À'] * 2,
    ['Á'] * 2,
    ['Ö'] * 2,
    ['Ø'] * 2,
    ['ö'] * 2,
    ['ø'] * 2,
    ['ÿ'] * 2,
    ['µ'] * 2,
    ['µ°F·Ω⁻¹', 'µ°F·Ω^-1'],
]


@pytest.mark.parametrize("_, unit_str, expected", multi_enumerate(not_udunits))
def test_invalid_in_udunits_but_still_parses(_, unit_str, expected):
    # Some units read fine in our grammar, but not in UDUNITS.

    try:
        cf_units.Unit(unit_str)
        cf_valid = True
    except ValueError:
        cf_valid = False

    # Double check that udunits2 can't parse this.
    assert cf_valid is False

    unit_expr = normalize(unit_str)
    assert unit_expr == expected


known_issues = [
    # Disabled due to crazy results from UDUNITS.
    ['s since +1990 +2:0:2.9', SyntaxError],
    ['s since -1990 +2:0:2.9', SyntaxError],

    # The following are not yet implemented.
    ['hours since 2001-12-31 23:59:59.999UTC', SyntaxError],
    ['hours since 2001-12-31 23:59:59.999 Z', SyntaxError],
    ['hours since 2001-12-31 23:59:59.999 GMT', SyntaxError],
    ['0.1 lg(re 1 mW)', SyntaxError],
]


@pytest.mark.parametrize("_, unit_str, expected",
                         multi_enumerate(known_issues))
def test_known_issues(_, unit_str, expected):
    # Unfortunately the grammar is not perfect.
    # These are the cases that don't work yet but which do work with udunits.

    # Make sure udunits can read it.
    cf_units.Unit(unit_str).symbol

    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(SyntaxError):
            unit_expr = normalize(unit_str)
    else:
        unit_expr = normalize(unit_str)
        assert unit_expr != expected


def test_syntax_parse_error_quality():
    # Check that the syntax error is giving us good context.

    msg = re.escape(r"no viable alternative at input 'm^m' (inline, line 1)")
    with pytest.raises(SyntaxError, match=msg) as err:
        normalize('m^m 2s')
    # The problem is with the m after "^", so make sure the exception is
    # pointing at it (including the leading speechmark).
    assert err.value.offset == 4


def test_unknown_symbol_error():
    msg = re.escape(r"mismatched input '×' expecting <EOF>")
    with pytest.raises(SyntaxError, match=msg) as err:
        # The × character is explicitly excluded in the UDUNITS2
        # implementation. It would make some sense to support it in the
        # future though.
        normalize('Thing×Another')
    # The 7th character (including the speechmark) is the problem, check that
    # the exception points at the right location.
    # correct location...
    #  File "inline", line 1
    #  'Thing×Another'
    #        ^
    assert err.value.offset == 7


not_allowed = [
    'hours from 1990-1-1 -20:4:18 +2',
    'm++2',
    'm s^(-1)',
    'm per /s',
]


@pytest.mark.parametrize("_, unit_str", enumerate(not_allowed))
def test_invalid_syntax_units(_, unit_str):
    # Check that units that aren't allowed with UDUNITS-2 are also not
    # allowed with our grammar.

    with pytest.raises(ValueError):
        cf_units.Unit(unit_str).symbol

    with pytest.raises(SyntaxError):
        normalize(unit_str)
