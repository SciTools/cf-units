# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""Test method :meth:`cf_units.Unit.date2num`."""

import cftime
import pytest

import cf_units

CALENDAR_CONSTANTS = [
    cf_units.CALENDAR_STANDARD,
    cf_units.CALENDAR_360_DAY,
    cf_units.CALENDAR_365_DAY,
]

CALENDAR_STRINGS = ["standard", "360_day", "365_day"]


@pytest.mark.parametrize(
    "calendar_const, calendar_str",
    zip(CALENDAR_CONSTANTS, CALENDAR_STRINGS, strict=False),
)
def test_fractional_second(calendar_const, calendar_str):
    unit = cf_units.Unit("seconds since 1970-01-01", calendar_const)
    dates = [
        cftime.datetime(1970, 1, 1, 0, 0, 0, 250000, calendar=calendar_str),
        cftime.datetime(1970, 1, 1, 0, 0, 0, 500000, calendar=calendar_str),
        cftime.datetime(1970, 1, 1, 0, 0, 0, 750000, calendar=calendar_str),
        cftime.datetime(1970, 1, 1, 0, 0, 1, 500000, calendar=calendar_str),
        cftime.datetime(1970, 1, 1, 0, 0, 2, 500000, calendar=calendar_str),
        cftime.datetime(1970, 1, 1, 0, 0, 3, 500000, calendar=calendar_str),
        cftime.datetime(1970, 1, 1, 0, 0, 4, 500000, calendar=calendar_str),
        cftime.datetime(1970, 1, 3, 0, 0, 4, 500000, calendar=calendar_str),
    ]
    nums = [0.25, 0.5, 0.75, 1.5, 2.5, 3.5, 4.5, 172804.5]

    for num, date in zip(nums, dates, strict=False):
        res = unit.date2num(date)
        assert num == pytest.approx(res)
