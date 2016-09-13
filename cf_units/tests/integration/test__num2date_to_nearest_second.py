# (C) British Crown Copyright 2016, Met Office
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
import netcdftime

from cf_units import _num2date_to_nearest_second, Unit


class Test(unittest.TestCase):
    def setup_units(self, calendar):
        self.useconds = netcdftime.utime('seconds since 1970-01-01',  calendar)
        self.uminutes = netcdftime.utime('minutes since 1970-01-01', calendar)
        self.uhours = netcdftime.utime('hours since 1970-01-01', calendar)
        self.udays = netcdftime.utime('days since 1970-01-01', calendar)

    def check_dates(self, nums, utimes, expected):
        for num, utime, exp in zip(nums, utimes, expected):
            res = _num2date_to_nearest_second(num, utime)
            self.assertEqual(exp, res)

    def test_scalar(self):
        utime = netcdftime.utime('seconds since 1970-01-01',  'gregorian')
        num = 5.
        exp = datetime.datetime(1970, 1, 1, 0, 0, 5)
        res = _num2date_to_nearest_second(num, utime)
        self.assertEqual(exp, res)

    def test_sequence(self):
        utime = netcdftime.utime('seconds since 1970-01-01',  'gregorian')
        nums = [20., 40., 60., 80, 100.]
        exp = [datetime.datetime(1970, 1, 1, 0, 0, 20),
               datetime.datetime(1970, 1, 1, 0, 0, 40),
               datetime.datetime(1970, 1, 1, 0, 1),
               datetime.datetime(1970, 1, 1, 0, 1, 20),
               datetime.datetime(1970, 1, 1, 0, 1, 40)]
        res = _num2date_to_nearest_second(nums, utime)
        np.testing.assert_array_equal(exp, res)

    def test_iter(self):
        utime = netcdftime.utime('seconds since 1970-01-01',  'gregorian')
        nums = iter([5., 10.])
        exp = [datetime.datetime(1970, 1, 1, 0, 0, 5),
               datetime.datetime(1970, 1, 1, 0, 0, 10)]
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
        expected = [netcdftime.datetime(1970, 1, 1, 0, 0, 20),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 40),
                    netcdftime.datetime(1970, 1, 1, 1, 15),
                    netcdftime.datetime(1970, 1, 1, 2, 30),
                    netcdftime.datetime(1970, 1, 1, 8),
                    netcdftime.datetime(1970, 1, 1, 16),
                    netcdftime.datetime(1970, 11, 1),
                    netcdftime.datetime(1971, 9, 1)]

        self.check_dates(nums, utimes, expected)

    def test_fractional_360_day(self):
        self.setup_units('360_day')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        utimes = [self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]
        expected = [netcdftime.datetime(1970, 1, 1, 0, 0, 5),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 10),
                    netcdftime.datetime(1970, 1, 1, 0, 15),
                    netcdftime.datetime(1970, 1, 1, 0, 30),
                    netcdftime.datetime(1970, 1, 1, 8),
                    netcdftime.datetime(1970, 1, 1, 16)]

        self.check_dates(nums, utimes, expected)

    def test_fractional_second_360_day(self):
        self.setup_units('360_day')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        utimes = [self.useconds] * 7
        expected = [netcdftime.datetime(1970, 1, 1, 0, 0, 0),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 1),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 1),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 2),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 3),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 4),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 5)]

        self.check_dates(nums, utimes, expected)

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
        expected = [netcdftime.datetime(1970, 1, 1, 0, 0, 20),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 40),
                    netcdftime.datetime(1970, 1, 1, 1, 15),
                    netcdftime.datetime(1970, 1, 1, 2, 30),
                    netcdftime.datetime(1970, 1, 1, 8),
                    netcdftime.datetime(1970, 1, 1, 16),
                    netcdftime.datetime(1970, 10, 28),
                    netcdftime.datetime(1971, 8, 24)]

        self.check_dates(nums, utimes, expected)

    def test_fractional_365_day(self):
        self.setup_units('365_day')
        nums = [5./60., 10./60.,
                15./60., 30./60.,
                8./24., 16./24.]
        utimes = [self.uminutes, self.uminutes,
                  self.uhours, self.uhours,
                  self.udays, self.udays]

        expected = [netcdftime.datetime(1970, 1, 1, 0, 0, 5),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 10),
                    netcdftime.datetime(1970, 1, 1, 0, 15),
                    netcdftime.datetime(1970, 1, 1, 0, 30),
                    netcdftime.datetime(1970, 1, 1, 8),
                    netcdftime.datetime(1970, 1, 1, 16)]

        self.check_dates(nums, utimes, expected)

    def test_fractional_second_365_day(self):
        self.setup_units('365_day')
        nums = [0.25, 0.5, 0.75,
                1.5, 2.5, 3.5, 4.5]
        utimes = [self.useconds] * 7
        expected = [netcdftime.datetime(1970, 1, 1, 0, 0, 0),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 1),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 1),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 2),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 3),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 4),
                    netcdftime.datetime(1970, 1, 1, 0, 0, 5)]

        self.check_dates(nums, utimes, expected)

if __name__ == '__main__':
    unittest.main()
