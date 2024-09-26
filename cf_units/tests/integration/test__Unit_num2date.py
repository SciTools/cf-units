# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""Test method :meth:`cf_units.Unit.num2date`."""

import datetime

import cftime
import numpy as np
import pytest

import cf_units


class Test:
    def setup_units(self, calendar):
        self.useconds = cf_units.Unit("seconds since 1970-01-01", calendar)
        self.uminutes = cf_units.Unit("minutes since 1970-01-01", calendar)
        self.uhours = cf_units.Unit("hours since 1970-01-01", calendar)
        self.udays = cf_units.Unit("days since 1970-01-01", calendar)

    def check_dates(self, nums, units, expected, only_cftime=True):
        for num, unit, exp in zip(nums, units, expected, strict=False):
            res = unit.num2date(num, only_use_cftime_datetimes=only_cftime)
            assert exp == res
            assert isinstance(res, type(exp))

    def check_timedelta(self, nums, units, expected):
        for num, unit, exp in zip(nums, units, expected, strict=False):
            epoch = cftime.num2date(0, unit.cftime_unit, unit.calendar)
            res = unit.num2date(num)
            delta = res - epoch
            assert (delta.days, delta.seconds, delta.microseconds) == exp

    def test_scalar(self):
        unit = cf_units.Unit("seconds since 1970-01-01", "gregorian")
        num = 5.0
        exp = datetime.datetime(1970, 1, 1, 0, 0, 5)
        res = unit.num2date(num)
        assert exp == res
        assert isinstance(res, cftime.datetime)

    def test_sequence(self):
        unit = cf_units.Unit("seconds since 1970-01-01", "gregorian")
        nums = [20.0, 40.0, 60.0, 80, 100.0]
        exp = [
            datetime.datetime(1970, 1, 1, 0, 0, 20),
            datetime.datetime(1970, 1, 1, 0, 0, 40),
            datetime.datetime(1970, 1, 1, 0, 1),
            datetime.datetime(1970, 1, 1, 0, 1, 20),
            datetime.datetime(1970, 1, 1, 0, 1, 40),
        ]
        res = unit.num2date(nums)
        np.testing.assert_array_equal(exp, res)

    def test_multidim_sequence(self):
        unit = cf_units.Unit("seconds since 1970-01-01", "gregorian")
        nums = [[20.0, 40.0, 60.0], [80, 100.0, 120.0]]
        exp_shape = (2, 3)
        res = unit.num2date(nums)
        assert exp_shape == res.shape

    def test_masked_ndarray(self):
        unit = cf_units.Unit("seconds since 1970-01-01", "gregorian")
        nums = np.ma.masked_array([20.0, 40.0, 60.0], [False, True, False])
        exp = [
            datetime.datetime(1970, 1, 1, 0, 0, 20),
            None,
            datetime.datetime(1970, 1, 1, 0, 1),
        ]
        res = unit.num2date(nums)
        np.testing.assert_array_equal(exp, res)

    # Gregorian Calendar tests

    def test_simple_gregorian_py_datetime_type(self):
        self.setup_units("gregorian")
        nums = [20.0, 40.0, 75.0, 150.0, 8.0, 16.0, 300.0, 600.0]
        units = [
            self.useconds,
            self.useconds,
            self.uminutes,
            self.uminutes,
            self.uhours,
            self.uhours,
            self.udays,
            self.udays,
        ]
        expected = [
            datetime.datetime(1970, 1, 1, 0, 0, 20),
            datetime.datetime(1970, 1, 1, 0, 0, 40),
            datetime.datetime(1970, 1, 1, 1, 15),
            datetime.datetime(1970, 1, 1, 2, 30),
            datetime.datetime(1970, 1, 1, 8),
            datetime.datetime(1970, 1, 1, 16),
            datetime.datetime(1970, 10, 28),
            datetime.datetime(1971, 8, 24),
        ]

        self.check_dates(nums, units, expected, only_cftime=False)

    def test_simple_gregorian(self):
        self.setup_units("gregorian")
        nums = [20.0, 40.0, 75.0, 150.0, 8.0, 16.0, 300.0, 600.0]
        units = [
            self.useconds,
            self.useconds,
            self.uminutes,
            self.uminutes,
            self.uhours,
            self.uhours,
            self.udays,
            self.udays,
        ]
        expected = [
            cftime.datetime(1970, 1, 1, 0, 0, 20, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 40, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 1, 15, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 2, 30, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 8, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 16, calendar="gregorian"),
            cftime.datetime(1970, 10, 28, calendar="gregorian"),
            cftime.datetime(1971, 8, 24, calendar="gregorian"),
        ]

        self.check_dates(nums, units, expected)

    def test_fractional_gregorian(self):
        self.setup_units("gregorian")
        nums = [
            5.0 / 60.0,
            10.0 / 60.0,
            15.0 / 60.0,
            30.0 / 60.0,
            8.0 / 24.0,
            16.0 / 24.0,
        ]
        units = [
            self.uminutes,
            self.uminutes,
            self.uhours,
            self.uhours,
            self.udays,
            self.udays,
        ]
        expected = [
            cftime.datetime(1970, 1, 1, 0, 0, 5, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 10, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 15, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 30, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 8, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 16, calendar="gregorian"),
        ]

        self.check_dates(nums, units, expected)

    def test_fractional_second_gregorian(self):
        self.setup_units("gregorian")
        nums = [0.25, 0.5, 0.75, 1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        expected = [
            cftime.datetime(1970, 1, 1, 0, 0, 0, 250000, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 0, 500000, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 0, 750000, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 1, 500000, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 2, 500000, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 3, 500000, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 4, 500000, calendar="gregorian"),
        ]

        self.check_dates(nums, units, expected)

    # 360 day Calendar tests

    def test_simple_360_day(self):
        self.setup_units("360_day")
        nums = [20.0, 40.0, 75.0, 150.0, 8.0, 16.0, 300.0, 600.0]
        units = [
            self.useconds,
            self.useconds,
            self.uminutes,
            self.uminutes,
            self.uhours,
            self.uhours,
            self.udays,
            self.udays,
        ]
        # Expected results in (days, seconds, microseconds) delta from unit
        # epoch.
        expected = [
            (0, nums[0], 0),
            (0, nums[1], 0),
            (0, nums[2] * 60, 0),
            (0, nums[3] * 60, 0),
            (0, nums[4] * 60 * 60, 0),
            (0, nums[5] * 60 * 60, 0),
            (nums[6], 0, 0),
            (nums[7], 0, 0),
        ]

        self.check_timedelta(nums, units, expected)

    def test_fractional_360_day(self):
        self.setup_units("360_day")
        nums = [
            5.0 / 60.0,
            10.0 / 60.0,
            15.0 / 60.0,
            30.0 / 60.0,
            8.0 / 24.0,
            16.0 / 24.0,
        ]
        units = [
            self.uminutes,
            self.uminutes,
            self.uhours,
            self.uhours,
            self.udays,
            self.udays,
        ]
        # Expected results in (days, seconds, microseconds) delta from unit
        # epoch.
        expected = [
            (0, nums[0] * 60, 0),
            (0, nums[1] * 60, 0),
            (0, nums[2] * 60 * 60, 0),
            (0, nums[3] * 60 * 60, 0),
            (0, nums[4] * 24 * 60 * 60, 0),
            (0, nums[5] * 24 * 60 * 60, 0),
        ]

        self.check_timedelta(nums, units, expected)

    def test_fractional_second_360_day(self):
        self.setup_units("360_day")
        nums = [0.25, 0.5, 0.75, 1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        # Expected results in (days, seconds, microseconds) delta from unit
        # epoch.
        expected = [
            (0, 0, 250000),
            (0, 0, 500000),
            (0, 0, 750000),
            (0, 1, 500000),
            (0, 2, 500000),
            (0, 3, 500000),
            (0, 4, 500000),
        ]

        self.check_timedelta(nums, units, expected)

    def test_pydatetime_wrong_calendar(self):
        unit = cf_units.Unit("days since 1970-01-01", calendar="360_day")
        with pytest.raises(
            ValueError, match="illegal calendar or reference date"
        ):
            unit.num2date(
                1,
                only_use_cftime_datetimes=False,
                only_use_python_datetimes=True,
            )

    # 365 day Calendar tests

    def test_simple_365_day(self):
        self.setup_units("365_day")
        nums = [20.0, 40.0, 75.0, 150.0, 8.0, 16.0, 300.0, 600.0]
        units = [
            self.useconds,
            self.useconds,
            self.uminutes,
            self.uminutes,
            self.uhours,
            self.uhours,
            self.udays,
            self.udays,
        ]
        # Expected results in (days, seconds, microseconds) delta from unit
        # epoch.
        expected = [
            (0, nums[0], 0),
            (0, nums[1], 0),
            (0, nums[2] * 60, 0),
            (0, nums[3] * 60, 0),
            (0, nums[4] * 60 * 60, 0),
            (0, nums[5] * 60 * 60, 0),
            (nums[6], 0, 0),
            (nums[7], 0, 0),
        ]

        self.check_timedelta(nums, units, expected)

    def test_fractional_365_day(self):
        self.setup_units("365_day")
        nums = [
            5.0 / 60.0,
            10.0 / 60.0,
            15.0 / 60.0,
            30.0 / 60.0,
            8.0 / 24.0,
            16.0 / 24.0,
        ]
        units = [
            self.uminutes,
            self.uminutes,
            self.uhours,
            self.uhours,
            self.udays,
            self.udays,
        ]
        # Expected results in (days, seconds, microseconds) delta from unit
        # epoch.
        expected = [
            (0, nums[0] * 60, 0),
            (0, nums[1] * 60, 0),
            (0, nums[2] * 60 * 60, 0),
            (0, nums[3] * 60 * 60, 0),
            (0, nums[4] * 24 * 60 * 60, 0),
            (0, nums[5] * 24 * 60 * 60, 0),
        ]

        self.check_timedelta(nums, units, expected)

    def test_fractional_second_365_day(self):
        self.setup_units("365_day")
        nums = [0.25, 0.5, 0.75, 1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        # Expected results in (days, seconds, microseconds) delta from unit
        # epoch.
        expected = [
            (0, 0, 250000),
            (0, 0, 500000),
            (0, 0, 750000),
            (0, 1, 500000),
            (0, 2, 500000),
            (0, 3, 500000),
            (0, 4, 500000),
        ]

        self.check_timedelta(nums, units, expected)
