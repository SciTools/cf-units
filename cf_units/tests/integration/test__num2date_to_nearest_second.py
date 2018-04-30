# (C) British Crown Copyright 2016 - 2018, Met Office
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
"""Test function :func:`cf_units._num2date_to_nearest_second`."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import unittest
import datetime

import numpy as np
import numpy.testing
import cftime

from cf_units import _num2date_to_nearest_second, Unit


class Test(unittest.TestCase):
    def setup_units(self, calendar):
        self.useconds = cftime.utime('seconds since 1970-01-01',  calendar)
        self.uminutes = cftime.utime('minutes since 1970-01-01', calendar)
        self.uhours = cftime.utime('hours since 1970-01-01', calendar)
        self.udays = cftime.utime('days since 1970-01-01', calendar)

    def check_dates(self, nums, utimes, expected):
        for num, utime, exp in zip(nums, utimes, expected):
            res = _num2date_to_nearest_second(num, utime)
            self.assertEqual(exp, res)

    def check_timedelta(self, nums, utimes, expected):
        for num, utime, exp in zip(nums, utimes, expected):
            epoch = utime.num2date(0)
            res = _num2date_to_nearest_second(num, utime)
            delta = res - epoch
            seconds = np.round(delta.seconds + (delta.microseconds / 1000000))
            self.assertEqual((delta.days, seconds), exp)

    def test_scalar(self):
        utime = cftime.utime('seconds since 1970-01-01',  'gregorian')
        num = 5.
        exp = datetime.datetime(1970, 1, 1, 0, 0, 5)
        res = _num2date_to_nearest_second(num, utime)
        self.assertEqual(exp, res)

    def test_sequence(self):
        utime = cftime.utime('seconds since 1970-01-01',  'gregorian')
        nums = [20., 40., 60., 80, 100.]
        exp = [datetime.datetime(1970, 1, 1, 0, 0, 20),
               datetime.datetime(1970, 1, 1, 0, 0, 40),
               datetime.datetime(1970, 1, 1, 0, 1),
               datetime.datetime(1970, 1, 1, 0, 1, 20),
               datetime.datetime(1970, 1, 1, 0, 1, 40)]
        res = _num2date_to_nearest_second(nums, utime)
        np.testing.assert_array_equal(exp, res)

    def test_multidim_sequence(self):
        utime = cftime.utime('seconds since 1970-01-01',  'gregorian')
        nums = [[20., 40., 60.],
                [80, 100., 120.]]
        exp_shape = (2, 3)
        res = _num2date_to_nearest_second(nums, utime)
        self.assertEqual(exp_shape, res.shape)

    def test_masked_ndarray(self):
        utime = cftime.utime('seconds since 1970-01-01',  'gregorian')
        nums = np.ma.masked_array([20., 40., 60.], [False, True, False])
        exp = [datetime.datetime(1970, 1, 1, 0, 0, 20),
               None,
               datetime.datetime(1970, 1, 1, 0, 1)]
        res = _num2date_to_nearest_second(nums, utime)
        np.testing.assert_array_equal(exp, res)

    # Gregorian Calendar tests

    def test_simple_gregorian(self):
        self.setup_units('gregorian')
        nums = [20., 40.,
                75., 150.,
                8., 16.,
                300., 600.]
        utimes = [self.useconds, self.useconds,
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

        self.check_dates(nums, utimes, expected)

    def test_fractional_gregorian(self):
        self.setup_units('gregorian')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        utimes = [self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        expected = [datetime.datetime(1970, 1, 1, 0, 0, 5),
                    datetime.datetime(1970, 1, 1, 0, 0, 10),
                    datetime.datetime(1970, 1, 1, 0, 15),
                    datetime.datetime(1970, 1, 1, 0, 30),
                    datetime.datetime(1970, 1, 1, 8),
                    datetime.datetime(1970, 1, 1, 16)]

        self.check_dates(nums, utimes, expected)

    def test_fractional_second_gregorian(self):
        self.setup_units('gregorian')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        utimes = [self.useconds] * 7
        expected = [datetime.datetime(1970, 1, 1, 0, 0, 0),
                    datetime.datetime(1970, 1, 1, 0, 0, 1),
                    datetime.datetime(1970, 1, 1, 0, 0, 1),
                    datetime.datetime(1970, 1, 1, 0, 0, 2),
                    datetime.datetime(1970, 1, 1, 0, 0, 3),
                    datetime.datetime(1970, 1, 1, 0, 0, 4),
                    datetime.datetime(1970, 1, 1, 0, 0, 5)]

        self.check_dates(nums, utimes, expected)

    # 360 day Calendar tests

    def test_simple_360_day(self):
        self.setup_units('360_day')
        nums = [20., 40.,
                75., 150.,
                8., 16.,
                300., 600.]
        utimes = [self.useconds, self.useconds,
                  self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        # Expected results in (days, seconds) delta from utime epoch.
        expected = [(0, nums[0]),
                    (0, nums[1]),
                    (0, nums[2]*60),
                    (0, nums[3]*60),
                    (0, nums[4]*60*60),
                    (0, nums[5]*60*60),
                    (nums[6], 0),
                    (nums[7], 0)]

        self.check_timedelta(nums, utimes, expected)

    def test_fractional_360_day(self):
        self.setup_units('360_day')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        utimes = [self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        # Expected results in (days, seconds) delta from utime epoch.
        expected = [(0, nums[0]*60),
                    (0, nums[1]*60),
                    (0, nums[2]*60*60),
                    (0, nums[3]*60*60),
                    (0, nums[4]*24*60*60),
                    (0, nums[5]*24*60*60)]

        self.check_timedelta(nums, utimes, expected)

    def test_fractional_second_360_day(self):
        self.setup_units('360_day')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        utimes = [self.useconds] * 7
        # Expected results in (days, seconds) delta from utime epoch.
        expected = [(0, 0.0),  # rounded down to this
                    (0, 1.0),  # rounded up to this
                    (0, 1.0),  # rounded up to this
                    (0, 2.0),  # rounded up to this
                    (0, 3.0),  # rounded up to this
                    (0, 4.0),  # rounded up to this
                    (0, 5.0)]  # rounded up to this

        self.check_timedelta(nums, utimes, expected)

    # 365 day Calendar tests

    def test_simple_365_day(self):
        self.setup_units('365_day')
        nums = [20., 40.,
                75., 150.,
                8., 16.,
                300., 600.]
        utimes = [self.useconds, self.useconds,
                  self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        # Expected results in (days, seconds) delta from utime epoch.
        expected = [(0, nums[0]),
                    (0, nums[1]),
                    (0, nums[2]*60),
                    (0, nums[3]*60),
                    (0, nums[4]*60*60),
                    (0, nums[5]*60*60),
                    (nums[6], 0),
                    (nums[7], 0)]

        self.check_timedelta(nums, utimes, expected)

    def test_fractional_365_day(self):
        self.setup_units('365_day')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        utimes = [self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        # Expected results in (days, seconds) delta from utime epoch.
        expected = [(0, nums[0]*60),
                    (0, nums[1]*60),
                    (0, nums[2]*60*60),
                    (0, nums[3]*60*60),
                    (0, nums[4]*24*60*60),
                    (0, nums[5]*24*60*60)]

        self.check_timedelta(nums, utimes, expected)

    def test_fractional_second_365_day(self):
        self.setup_units('365_day')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        utimes = [self.useconds] * 7
        # Expected results in (days, seconds) delta from utime epoch.
        expected = [(0, 0.0),  # rounded down to this
                    (0, 1.0),  # rounded up to this
                    (0, 1.0),  # rounded up to this
                    (0, 2.0),  # rounded up to this
                    (0, 3.0),  # rounded up to this
                    (0, 4.0),  # rounded up to this
                    (0, 5.0)]  # rounded up to this

        self.check_timedelta(nums, utimes, expected)


if __name__ == '__main__':
    unittest.main()
