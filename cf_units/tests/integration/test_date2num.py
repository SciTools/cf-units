# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Test function :func:`cf_units.date2num`."""

import datetime
import unittest

import numpy as np

from cf_units import date2num


class Test(unittest.TestCase):
    def setUp(self):
        self.unit = "seconds since 1970-01-01"
        self.calendar = "gregorian"

    def test_single(self):
        date = datetime.datetime(1970, 1, 1, 0, 0, 5)
        exp = 5.0
        res = date2num(date, self.unit, self.calendar)
        # num2date won't return an exact value representing the date,
        # even if one exists
        self.assertAlmostEqual(exp, res, places=4)

    def test_sequence(self):
        dates = [
            datetime.datetime(1970, 1, 1, 0, 0, 20),
            datetime.datetime(1970, 1, 1, 0, 0, 40),
            datetime.datetime(1970, 1, 1, 0, 1),
            datetime.datetime(1970, 1, 1, 0, 1, 20),
            datetime.datetime(1970, 1, 1, 0, 1, 40),
        ]
        exp = [20.0, 40.0, 60.0, 80, 100.0]
        res = date2num(dates, self.unit, self.calendar)
        np.testing.assert_array_almost_equal(exp, res, decimal=4)

    def test_multidim_sequence(self):
        dates = [
            [
                datetime.datetime(1970, 1, 1, 0, 0, 20),
                datetime.datetime(1970, 1, 1, 0, 0, 40),
                datetime.datetime(1970, 1, 1, 0, 1),
            ],
            [
                datetime.datetime(1970, 1, 1, 0, 1, 20),
                datetime.datetime(1970, 1, 1, 0, 1, 40),
                datetime.datetime(1970, 1, 1, 0, 2),
            ],
        ]
        exp_shape = (2, 3)
        res = date2num(dates, self.unit, self.calendar)
        self.assertEqual(exp_shape, res.shape)

    def test_discard_mircosecond(self):
        date = datetime.datetime(1970, 1, 1, 0, 0, 5, 750000)
        exp = 5.0
        res = date2num(date, self.unit, self.calendar)

        self.assertAlmostEqual(exp, res, places=4)

    def test_long_time_interval(self):
        # This test should fail with an error that we need to catch properly.
        unit = "years since 1970-01-01"
        date = datetime.datetime(1970, 1, 1, 0, 0, 5)
        exp_emsg = 'interval of "months", "years" .* got "years".'
        with self.assertRaisesRegex(ValueError, exp_emsg):
            date2num(date, unit, self.calendar)


if __name__ == "__main__":
    unittest.main()
