# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Test function :func:`cf_units._num2date_to_nearest_second`."""

import datetime
import unittest

import cftime
import numpy as np

import cf_units
from cf_units import _num2date_to_nearest_second


class Test(unittest.TestCase):
    def setup_units(self, calendar):
        self.useconds = cf_units.Unit("seconds since 1970-01-01", calendar)
        self.uminutes = cf_units.Unit("minutes since 1970-01-01", calendar)
        self.uhours = cf_units.Unit("hours since 1970-01-01", calendar)
        self.udays = cf_units.Unit("days since 1970-01-01", calendar)

    def check_dates(self, nums, units, expected, only_cftime=True):
        for num, unit, exp in zip(nums, units, expected):
            res = _num2date_to_nearest_second(
                num, unit, only_use_cftime_datetimes=only_cftime
            )
            self.assertEqual(exp, res)
            self.assertIsInstance(res, type(exp))

    def check_timedelta(self, nums, units, expected):
        for num, unit, exp in zip(nums, units, expected):
            epoch = cftime.num2date(0, unit.cftime_unit, unit.calendar)
            res = _num2date_to_nearest_second(num, unit)
            delta = res - epoch
            seconds = np.round(delta.seconds + (delta.microseconds / 1000000))
            self.assertEqual((delta.days, seconds), exp)

    def test_scalar(self):
        unit = cf_units.Unit("seconds since 1970-01-01", "gregorian")
        num = 5.0
        exp = datetime.datetime(1970, 1, 1, 0, 0, 5)
        res = _num2date_to_nearest_second(num, unit)
        self.assertEqual(exp, res)
        self.assertIsInstance(res, cftime.datetime)

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
        res = _num2date_to_nearest_second(nums, unit)
        np.testing.assert_array_equal(exp, res)

    def test_multidim_sequence(self):
        unit = cf_units.Unit("seconds since 1970-01-01", "gregorian")
        nums = [[20.0, 40.0, 60.0], [80, 100.0, 120.0]]
        exp_shape = (2, 3)
        res = _num2date_to_nearest_second(nums, unit)
        self.assertEqual(exp_shape, res.shape)

    def test_masked_ndarray(self):
        unit = cf_units.Unit("seconds since 1970-01-01", "gregorian")
        nums = np.ma.masked_array([20.0, 40.0, 60.0], [False, True, False])
        exp = [
            datetime.datetime(1970, 1, 1, 0, 0, 20),
            None,
            datetime.datetime(1970, 1, 1, 0, 1),
        ]
        res = _num2date_to_nearest_second(nums, unit)
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
            cftime.datetime(1970, 1, 1, 0, 0, 0, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 1, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 1, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 2, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 3, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 4, calendar="gregorian"),
            cftime.datetime(1970, 1, 1, 0, 0, 5, calendar="gregorian"),
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
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [
            (0, nums[0]),
            (0, nums[1]),
            (0, nums[2] * 60),
            (0, nums[3] * 60),
            (0, nums[4] * 60 * 60),
            (0, nums[5] * 60 * 60),
            (nums[6], 0),
            (nums[7], 0),
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
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [
            (0, nums[0] * 60),
            (0, nums[1] * 60),
            (0, nums[2] * 60 * 60),
            (0, nums[3] * 60 * 60),
            (0, nums[4] * 24 * 60 * 60),
            (0, nums[5] * 24 * 60 * 60),
        ]

        self.check_timedelta(nums, units, expected)

    def test_fractional_second_360_day(self):
        self.setup_units("360_day")
        nums = [0.25, 0.5, 0.75, 1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [
            (0, 0.0),  # rounded down to this
            (0, 1.0),  # rounded up to this
            (0, 1.0),  # rounded up to this
            (0, 2.0),  # rounded up to this
            (0, 3.0),  # rounded up to this
            (0, 4.0),  # rounded up to this
            (0, 5.0),
        ]  # rounded up to this

        self.check_timedelta(nums, units, expected)

    def test_pydatetime_wrong_calendar(self):
        unit = cf_units.Unit("days since 1970-01-01", calendar="360_day")
        with self.assertRaisesRegex(
            ValueError, "illegal calendar or reference date"
        ):
            _num2date_to_nearest_second(
                1,
                unit,
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
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [
            (0, nums[0]),
            (0, nums[1]),
            (0, nums[2] * 60),
            (0, nums[3] * 60),
            (0, nums[4] * 60 * 60),
            (0, nums[5] * 60 * 60),
            (nums[6], 0),
            (nums[7], 0),
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
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [
            (0, nums[0] * 60),
            (0, nums[1] * 60),
            (0, nums[2] * 60 * 60),
            (0, nums[3] * 60 * 60),
            (0, nums[4] * 24 * 60 * 60),
            (0, nums[5] * 24 * 60 * 60),
        ]

        self.check_timedelta(nums, units, expected)

    def test_fractional_second_365_day(self):
        self.setup_units("365_day")
        nums = [0.25, 0.5, 0.75, 1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [
            (0, 0.0),  # rounded down to this
            (0, 1.0),  # rounded up to this
            (0, 1.0),  # rounded up to this
            (0, 2.0),  # rounded up to this
            (0, 3.0),  # rounded up to this
            (0, 4.0),  # rounded up to this
            (0, 5.0),
        ]  # rounded up to this

        self.check_timedelta(nums, units, expected)


if __name__ == "__main__":
    unittest.main()
