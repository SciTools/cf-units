# (C) British Crown Copyright 2016 - 2019, Met Office
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
"""Test function :func:`cf_units.date2num`."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import unittest
import datetime

import numpy as np
import six

from cf_units import date2num


class Test(unittest.TestCase):
    def setUp(self):
        self.unit = 'seconds since 1970-01-01'
        self.calendar = 'gregorian'

    def test_single(self):
        date = datetime.datetime(1970, 1, 1, 0, 0, 5)
        exp = 5.
        res = date2num(date, self.unit, self.calendar)
        # num2date won't return an exact value representing the date,
        # even if one exists
        self.assertAlmostEqual(exp, res, places=4)

    def test_sequence(self):
        dates = [datetime.datetime(1970, 1, 1, 0, 0, 20),
                 datetime.datetime(1970, 1, 1, 0, 0, 40),
                 datetime.datetime(1970, 1, 1, 0, 1),
                 datetime.datetime(1970, 1, 1, 0, 1, 20),
                 datetime.datetime(1970, 1, 1, 0, 1, 40)]
        exp = [20., 40., 60., 80, 100.]
        res = date2num(dates, self.unit, self.calendar)
        np.testing.assert_array_almost_equal(exp, res, decimal=4)

    def test_multidim_sequence(self):
        dates = [[datetime.datetime(1970, 1, 1, 0, 0, 20),
                  datetime.datetime(1970, 1, 1, 0, 0, 40),
                  datetime.datetime(1970, 1, 1, 0, 1)],
                 [datetime.datetime(1970, 1, 1, 0, 1, 20),
                  datetime.datetime(1970, 1, 1, 0, 1, 40),
                  datetime.datetime(1970, 1, 1, 0, 2)]]
        exp_shape = (2, 3)
        res = date2num(dates, self.unit, self.calendar)
        self.assertEqual(exp_shape, res.shape)

    def test_discard_mircosecond(self):
        date = datetime.datetime(1970, 1, 1, 0, 0, 5, 750000)
        exp = 5.
        res = date2num(date, self.unit, self.calendar)

        self.assertAlmostEqual(exp, res, places=4)

    def test_long_time_interval(self):
        # This test should fail with an error that we need to catch properly.
        unit = 'years since 1970-01-01'
        date = datetime.datetime(1970, 1, 1, 0, 0, 5)
        exp_emsg = 'interval of "months", "years" .* got "years".'
        with six.assertRaisesRegex(self, ValueError, exp_emsg):
            date2num(date, unit, self.calendar)


if __name__ == '__main__':
    unittest.main()
