# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""Test method :meth:`cf_units.Unit.date2num`."""


import cftime
import pytest

import cf_units


def test_fractional_second_gregorian():
    nums = [0.25, 0.5, 0.75, 1.5, 2.5, 3.5, 4.5]
    unit = cf_units.Unit(
        "seconds since 1970-01-01", cf_units.CALENDAR_GREGORIAN
    )
    dates = [
        cftime.datetime(1970, 1, 1, 0, 0, 0, 250000, calendar="gregorian"),
        cftime.datetime(1970, 1, 1, 0, 0, 0, 500000, calendar="gregorian"),
        cftime.datetime(1970, 1, 1, 0, 0, 0, 750000, calendar="gregorian"),
        cftime.datetime(1970, 1, 1, 0, 0, 1, 500000, calendar="gregorian"),
        cftime.datetime(1970, 1, 1, 0, 0, 2, 500000, calendar="gregorian"),
        cftime.datetime(1970, 1, 1, 0, 0, 3, 500000, calendar="gregorian"),
        cftime.datetime(1970, 1, 1, 0, 0, 4, 500000, calendar="gregorian"),
    ]

    for num, date in zip(nums, dates):
        res = unit.date2num(date)
        assert num == pytest.approx(res)
