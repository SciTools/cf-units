# (C) British Crown Copyright 2014, Met Office
#
# This file is part of cf_units.
#
# cf_units is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cf_units is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cf_units.  If not, see <http://www.gnu.org/licenses/>.
"""Unit tests for the `cf_units.as_unit` function."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import copy
import unittest

import mock

import cf_units
from cf_units import as_unit, Unit


class StubUnit(object):
    def __init__(self, calendar=None):
        self._calendar = str(calendar)

    def __str__(self):
        return self.origin

    @property
    def origin(self):
        return 'hours since 1970-01-01 00:00:00'

    @property
    def ut_unit(self):
        return 22943184

    @property
    def calendar(self):
        return self._calendar

    @property
    def category(self):
        return 2


class TestAll(unittest.TestCase):
    def _assert_unit_equal(self, unit1, unit2):
        # Custom equality assertion of units since equality of the Unit class
        # utilises as_unit.
        for attribute in ['origin', 'calendar', 'category']:
            self.assertEqual(getattr(unit1, attribute),
                             getattr(unit2, attribute))

    def test_cf_unit(self):
        unit = Unit('hours since 1970-01-01 00:00:00', calendar='360_day')
        target = copy.copy(unit)
        result = as_unit(unit)

        self._assert_unit_equal(result, target)
        self.assertIs(result, unit)

    def test_non_cf_unit_no_calendar(self):
        # Check that as_unit returns a default calendar (Gregorian)
        unit = StubUnit()
        target = copy.copy(unit)
        result = as_unit(unit)

        self.assertEqual(result.calendar, 'gregorian')

    def test_non_cf_unit_with_calendar(self):
        unit = StubUnit('360_day')
        target = copy.copy(unit)
        result = as_unit(unit)
        self._assert_unit_equal(result, target)


if __name__ == '__main__':
    unittest.main()
