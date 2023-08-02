# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""Test function :func:`cf_units.date2num`."""

import datetime

import numpy as np
import pytest

from cf_units import date2num


class Test:
    def setup_method(self):
        self.unit = "seconds since 1970-01-01"
        self.calendar = "gregorian"

    def test_single(self):
        date = datetime.datetime(1970, 1, 1, 0, 0, 5)
        exp = 5
        res = date2num(date, self.unit, self.calendar)

        assert exp == res

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
        assert exp_shape == res.shape

    def test_convert_microsecond(self):
        date = datetime.datetime(1970, 1, 1, 0, 0, 5, 750000)
        exp = 5.75
        res = date2num(date, self.unit, self.calendar)

        assert exp == pytest.approx(res)
