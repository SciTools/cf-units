# (C) British Crown Copyright 2016 - 2021, Met Office
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
"""Test function :func:`cf_units._num2date_to_nearest_second`."""

import unittest
import datetime

import numpy as np
import cftime

import cf_units
from cf_units import _num2date_to_nearest_second


class Test(unittest.TestCase):
    def setup_units(self, calendar):
        self.useconds = cf_units.Unit('seconds since 1970-01-01',  calendar)
        self.uminutes = cf_units.Unit('minutes since 1970-01-01', calendar)
        self.uhours = cf_units.Unit('hours since 1970-01-01', calendar)
        self.udays = cf_units.Unit('days since 1970-01-01', calendar)

    def check_dates(self, nums, units, expected, only_cftime=True):
        for num, unit, exp in zip(nums, units, expected):
            res = _num2date_to_nearest_second(
                num, unit, only_use_cftime_datetimes=only_cftime)
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
        unit = cf_units.Unit('seconds since 1970-01-01',  'gregorian')
        num = 5.
        exp = datetime.datetime(1970, 1, 1, 0, 0, 5)
        res = _num2date_to_nearest_second(num, unit)
        self.assertEqual(exp, res)
        self.assertIsInstance(res, cftime.DatetimeGregorian)

    def test_sequence(self):
        unit = cf_units.Unit('seconds since 1970-01-01',  'gregorian')
        nums = [20., 40., 60., 80, 100.]
        exp = [datetime.datetime(1970, 1, 1, 0, 0, 20),
               datetime.datetime(1970, 1, 1, 0, 0, 40),
               datetime.datetime(1970, 1, 1, 0, 1),
               datetime.datetime(1970, 1, 1, 0, 1, 20),
               datetime.datetime(1970, 1, 1, 0, 1, 40)]
        res = _num2date_to_nearest_second(nums, unit)
        np.testing.assert_array_equal(exp, res)

    def test_multidim_sequence(self):
        unit = cf_units.Unit('seconds since 1970-01-01',  'gregorian')
        nums = [[20., 40., 60.],
                [80, 100., 120.]]
        exp_shape = (2, 3)
        res = _num2date_to_nearest_second(nums, unit)
        self.assertEqual(exp_shape, res.shape)

    def test_masked_ndarray(self):
        unit = cf_units.Unit('seconds since 1970-01-01',  'gregorian')
        nums = np.ma.masked_array([20., 40., 60.], [False, True, False])
        exp = [datetime.datetime(1970, 1, 1, 0, 0, 20),
               None,
               datetime.datetime(1970, 1, 1, 0, 1)]
        res = _num2date_to_nearest_second(nums, unit)
        np.testing.assert_array_equal(exp, res)

    # Gregorian Calendar tests

    def test_simple_gregorian_py_datetime_type(self):
        self.setup_units('gregorian')
        nums = [20., 40.,
                75., 150.,
                8., 16.,
                300., 600.]
        units = [self.useconds, self.useconds,
                 self.uminutes, self.uminutes,
                 self.uhours, self.uhours,
                 self.udays, self.udays]
        expected = [datetime.datetime(1970, 1, 1, 0, 0, 20),
                    datetime.datetime(1970, 1, 1, 0, 0, 40),
                    datetime.datetime(1970, 1, 1, 1, 15),
                    datetime.datetime(1970, 1, 1, 2, 30),
                    datetime.datetime(1970, 1, 1, 8),
                    datetime.datetime(1970, 1, 1, 16),
                    datetime.datetime(1970, 10, 28),
                    datetime.datetime(1971, 8, 24)]

        self.check_dates(nums, units, expected, only_cftime=False)

    def test_simple_gregorian(self):
        self.setup_units('gregorian')
        nums = [20., 40.,
                75., 150.,
                8., 16.,
                300., 600.]
        units = [self.useconds, self.useconds,
                  self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        expected = [cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 20),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 40),
                    cftime.DatetimeGregorian(1970, 1, 1, 1, 15),
                    cftime.DatetimeGregorian(1970, 1, 1, 2, 30),
                    cftime.DatetimeGregorian(1970, 1, 1, 8),
                    cftime.DatetimeGregorian(1970, 1, 1, 16),
                    cftime.DatetimeGregorian(1970, 10, 28),
                    cftime.DatetimeGregorian(1971, 8, 24)]

        self.check_dates(nums, units, expected)

    def test_fractional_gregorian(self):
        self.setup_units('gregorian')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        units = [self.uminutes, self.uminutes,
                 self.uhours, self.uhours,
                 self.udays, self.udays]
        expected = [cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 5),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 10),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 15),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 30),
                    cftime.DatetimeGregorian(1970, 1, 1, 8),
                    cftime.DatetimeGregorian(1970, 1, 1, 16)]

        self.check_dates(nums, units, expected)

    def test_fractional_second_gregorian(self):
        self.setup_units('gregorian')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        expected = [cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 0),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 1),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 1),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 2),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 3),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 4),
                    cftime.DatetimeGregorian(1970, 1, 1, 0, 0, 5)]

        self.check_dates(nums, units, expected)

    # 360 day Calendar tests

    def test_simple_360_day(self):
        self.setup_units('360_day')
        nums = [20., 40.,
                75., 150.,
                8., 16.,
                300., 600.]
        units = [self.useconds, self.useconds,
                 self.uminutes, self.uminutes,
                 self.uhours, self.uhours,
                 self.udays, self.udays]
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [(0, nums[0]),
                    (0, nums[1]),
                    (0, nums[2]*60),
                    (0, nums[3]*60),
                    (0, nums[4]*60*60),
                    (0, nums[5]*60*60),
                    (nums[6], 0),
                    (nums[7], 0)]

        self.check_timedelta(nums, units, expected)

    def test_fractional_360_day(self):
        self.setup_units('360_day')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        units = [self.uminutes, self.uminutes,
                 self.uhours, self.uhours,
                 self.udays, self.udays]
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [(0, nums[0]*60),
                    (0, nums[1]*60),
                    (0, nums[2]*60*60),
                    (0, nums[3]*60*60),
                    (0, nums[4]*24*60*60),
                    (0, nums[5]*24*60*60)]

        self.check_timedelta(nums, units, expected)

    def test_fractional_second_360_day(self):
        self.setup_units('360_day')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [(0, 0.0),  # rounded down to this
                    (0, 1.0),  # rounded up to this
                    (0, 1.0),  # rounded up to this
                    (0, 2.0),  # rounded up to this
                    (0, 3.0),  # rounded up to this
                    (0, 4.0),  # rounded up to this
                    (0, 5.0)]  # rounded up to this

        self.check_timedelta(nums, units, expected)

    # 365 day Calendar tests

    def test_simple_365_day(self):
        self.setup_units('365_day')
        nums = [20., 40.,
                75., 150.,
                8., 16.,
                300., 600.]
        units = [self.useconds, self.useconds,
                  self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [(0, nums[0]),
                    (0, nums[1]),
                    (0, nums[2]*60),
                    (0, nums[3]*60),
                    (0, nums[4]*60*60),
                    (0, nums[5]*60*60),
                    (nums[6], 0),
                    (nums[7], 0)]

        self.check_timedelta(nums, units, expected)

    def test_fractional_365_day(self):
        self.setup_units('365_day')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        units = [self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [(0, nums[0]*60),
                    (0, nums[1]*60),
                    (0, nums[2]*60*60),
                    (0, nums[3]*60*60),
                    (0, nums[4]*24*60*60),
                    (0, nums[5]*24*60*60)]

        self.check_timedelta(nums, units, expected)

    def test_fractional_second_365_day(self):
        self.setup_units('365_day')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        units = [self.useconds] * 7
        # Expected results in (days, seconds) delta from unit epoch.
        expected = [(0, 0.0),  # rounded down to this
                    (0, 1.0),  # rounded up to this
                    (0, 1.0),  # rounded up to this
                    (0, 2.0),  # rounded up to this
                    (0, 3.0),  # rounded up to this
                    (0, 4.0),  # rounded up to this
                    (0, 5.0)]  # rounded up to this

        self.check_timedelta(nums, units, expected)


if __name__ == '__main__':
    unittest.main()
