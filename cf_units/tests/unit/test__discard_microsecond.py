# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Unit tests for the `cf_units._discard_microsecond` function."""

import datetime
import unittest

import cftime
import numpy as np
import numpy.ma as ma

from cf_units import _discard_microsecond as discard_microsecond


class Test__datetime(unittest.TestCase):
    def setUp(self):
        self.kwargs = dict(year=1, month=2, day=3, hour=4, minute=5, second=6)
        self.expected = datetime.datetime(**self.kwargs, microsecond=0)

    def test_single(self):
        dt = datetime.datetime(**self.kwargs, microsecond=7)
        actual = discard_microsecond(dt)
        self.assertEqual(self.expected, actual)

    def test_multi(self):
        shape = (5, 2)
        n = np.prod(shape)

        dates = np.array(
            [datetime.datetime(**self.kwargs, microsecond=i) for i in range(n)]
        ).reshape(shape)
        actual = discard_microsecond(dates)
        expected = np.array([self.expected] * n).reshape(shape)
        np.testing.assert_array_equal(expected, actual)


class Test__cftime(unittest.TestCase):
    def setUp(self):
        self.kwargs = dict(year=1, month=2, day=3, hour=4, minute=5, second=6)
        self.calendars = cftime._cftime._calendars

    def test_single(self):
        for calendar in self.calendars:
            dt = cftime.datetime(**self.kwargs, calendar=calendar)
            actual = discard_microsecond(dt)
            expected = cftime.datetime(
                **self.kwargs, microsecond=0, calendar=calendar
            )
            self.assertEqual(expected, actual)

    def test_multi(self):
        shape = (2, 5)
        n = np.prod(shape)

        for calendar in self.calendars:
            dates = np.array(
                [
                    cftime.datetime(**self.kwargs, calendar=calendar)
                    for i in range(n)
                ]
            ).reshape(shape)
            actual = discard_microsecond(dates)
            expected = np.array(
                [
                    cftime.datetime(
                        **self.kwargs, microsecond=0, calendar=calendar
                    )
                ]
                * n
            ).reshape(shape)
            np.testing.assert_array_equal(expected, actual)


class Test__falsy(unittest.TestCase):
    def setUp(self):
        self.kwargs = dict(year=1, month=2, day=3, hour=4, minute=5, second=6)
        self.calendar = "360_day"
        microsecond = 7
        self.cftime = cftime.datetime(
            **self.kwargs, microsecond=microsecond, calendar=self.calendar
        )
        self.datetime = datetime.datetime(
            **self.kwargs, microsecond=microsecond
        )

    def test_single__none(self):
        self.assertIsNone(discard_microsecond(None))

    def test_single__false(self):
        self.assertFalse(discard_microsecond(False))

    def test_multi__falsy(self):
        falsy = np.array([None, False, 0])
        actual = discard_microsecond(falsy)
        np.testing.assert_array_equal(falsy, actual)

    def test_masked(self):
        data = [self.cftime, self.datetime, self.cftime, self.datetime]
        mask = [1, 0, 0, 1]
        dates = ma.masked_array(data, mask=mask)
        actual = discard_microsecond(dates)
        expected = np.array(
            [
                ma.masked,
                datetime.datetime(**self.kwargs),
                cftime.datetime(**self.kwargs, calendar=self.calendar),
                ma.masked,
            ]
        )
        self.assertEqual(expected.shape, actual.shape)
        for i, masked in enumerate(mask):
            if masked:
                self.assertIs(expected[i], actual[i])
            else:
                self.assertEqual(expected[i], actual[i])


if __name__ == "__main__":
    unittest.main()
