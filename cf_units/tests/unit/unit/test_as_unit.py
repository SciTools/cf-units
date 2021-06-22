# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Unit tests for the `cf_units.as_unit` function."""

import copy
import unittest

from cf_units import Unit, as_unit


class StubUnit(object):
    def __init__(self, calendar=None):
        self.calendar = str(calendar) if calendar is not None else None
        # udunit category
        self.category = 2
        # ut_unit should be an integer but not under test
        self.ut_unit = 0
        self.origin = "hours since 1970-01-01 00:00:00"

    def __str__(self):
        return self.origin


class TestAll(unittest.TestCase):
    def _assert_unit_equal(self, unit1, unit2):
        # Custom equality assertion of units since equality of the Unit class
        # utilises as_unit.
        for attribute in ["origin", "calendar", "category"]:
            self.assertEqual(
                getattr(unit1, attribute), getattr(unit2, attribute)
            )

    def test_cf_unit(self):
        # Ensure that as_unit returns the same cf_unit.Unit object and
        # remains unchanged.
        unit = Unit("hours since 1970-01-01 00:00:00", calendar="360_day")
        target = copy.copy(unit)
        result = as_unit(unit)

        self._assert_unit_equal(result, target)
        self.assertIs(result, unit)

    def test_non_cf_unit_no_calendar(self):
        # On passing as_unit a cf_unit.Unit-like object (not a cf_unit.Unit
        # object) with no calendar, ensure that a cf_unit.Unit is returned
        # with default calendar (Gregorian).
        unit = StubUnit()
        result = as_unit(unit)

        self.assertEqual(result.calendar, "gregorian")
        self.assertIsInstance(result, Unit)

    def test_non_cf_unit_with_calendar(self):
        # On passing as_unit a cf_unit.Unit-like object (not a cf_unit.Unit
        # object) with calendar, ensure that a cf_unit.Unit is returned
        # with the same calendar specified in the original unit-like object.
        unit = StubUnit("360_day")
        target = copy.copy(unit)
        result = as_unit(unit)
        self._assert_unit_equal(result, target)


if __name__ == "__main__":
    unittest.main()
