# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Unit tests for the `cf_units.Unit` class."""

import unittest

import numpy as np

import cf_units
from cf_units import Unit


class Test___init__(unittest.TestCase):
    def test_capitalised_calendar(self):
        calendar = "GrEgoRian"
        expected = cf_units.CALENDAR_GREGORIAN
        u = Unit("hours since 1970-01-01 00:00:00", calendar=calendar)
        self.assertEqual(u.calendar, expected)

    def test_not_basestring_calendar(self):
        with self.assertRaises(TypeError):
            Unit("hours since 1970-01-01 00:00:00", calendar=5)

    def test_hash_replacement(self):
        hash_unit = "m # s-1"
        expected = "m 1 s-1"
        u = Unit(hash_unit)
        self.assertEqual(u, expected)


class Test_convert__calendar(unittest.TestCase):
    class MyStr(str):
        pass

    def test_gregorian_calendar_conversion_setup(self):
        # Reproduces a situation where a unit's gregorian calendar would not
        # match (using the `is` operator) to the literal string 'gregorian',
        # causing an `is not` test to return a false negative.
        cal_str = cf_units.CALENDAR_GREGORIAN
        calendar = self.MyStr(cal_str)
        self.assertIsNot(calendar, cal_str)
        u1 = Unit("hours since 1970-01-01 00:00:00", calendar=calendar)
        u2 = Unit("hours since 1969-11-30 00:00:00", calendar=calendar)
        u1point = np.array([8.0], dtype=np.float32)
        expected = np.array([776.0], dtype=np.float32)
        result = u1.convert(u1point, u2)
        return expected, result

    def test_gregorian_calendar_conversion_array(self):
        expected, result = self.test_gregorian_calendar_conversion_setup()
        np.testing.assert_array_equal(expected, result)

    def test_gregorian_calendar_conversion_dtype(self):
        expected, result = self.test_gregorian_calendar_conversion_setup()
        self.assertEqual(expected.dtype, result.dtype)

    def test_gregorian_calendar_conversion_shape(self):
        expected, result = self.test_gregorian_calendar_conversion_setup()
        self.assertEqual(expected.shape, result.shape)

    def test_non_gregorian_calendar_conversion_dtype(self):
        for start_dtype, exp_convert in (
            (np.float32, True),
            (np.float64, True),
            (np.int32, False),
            (np.int64, False),
            (int, False),
        ):
            data = np.arange(4, dtype=start_dtype)
            u1 = Unit("hours since 2000-01-01 00:00:00", calendar="360_day")
            u2 = Unit("hours since 2000-01-02 00:00:00", calendar="360_day")
            result = u1.convert(data, u2)

            if exp_convert:
                self.assertEqual(result.dtype, start_dtype)
            else:
                self.assertEqual(result.dtype, np.int64)


class Test_convert__endianness_time(unittest.TestCase):
    # Test the behaviour of converting time units of differing
    # dtype endianness.

    def setUp(self):
        self.time1_array = np.array([31.5, 32.5, 33.5])
        self.time2_array = np.array([0.5, 1.5, 2.5])
        self.time1_unit = cf_units.Unit(
            "days since 1970-01-01 00:00:00",
            calendar=cf_units.CALENDAR_STANDARD,
        )
        self.time2_unit = cf_units.Unit(
            "days since 1970-02-01 00:00:00",
            calendar=cf_units.CALENDAR_STANDARD,
        )

    def test_no_endian(self):
        dtype = "f8"
        result = self.time1_unit.convert(
            self.time1_array.astype(dtype), self.time2_unit
        )
        np.testing.assert_array_almost_equal(result, self.time2_array)

    def test_little_endian(self):
        dtype = "<f8"
        result = self.time1_unit.convert(
            self.time1_array.astype(dtype), self.time2_unit
        )
        np.testing.assert_array_almost_equal(result, self.time2_array)

    def test_big_endian(self):
        dtype = ">f8"
        result = self.time1_unit.convert(
            self.time1_array.astype(dtype), self.time2_unit
        )
        np.testing.assert_array_almost_equal(result, self.time2_array)


class Test_convert__endianness_deg_to_rad(unittest.TestCase):
    # Test the behaviour of converting radial units of differing
    # dtype endianness.

    def setUp(self):
        self.degs_array = np.array([356.7, 356.8, 356.9])
        self.rads_array = np.array([6.22558944, 6.22733477, 6.2290801])
        self.deg = cf_units.Unit("degrees")
        self.rad = cf_units.Unit("radians")

    def test_no_endian(self):
        dtype = "f8"
        result = self.deg.convert(self.degs_array.astype(dtype), self.rad)
        np.testing.assert_array_almost_equal(result, self.rads_array)

    def test_little_endian(self):
        dtype = "<f8"
        result = self.deg.convert(self.degs_array.astype(dtype), self.rad)
        np.testing.assert_array_almost_equal(result, self.rads_array)

    def test_big_endian(self):
        dtype = ">f8"
        result = self.deg.convert(self.degs_array.astype(dtype), self.rad)
        np.testing.assert_array_almost_equal(result, self.rads_array)


class Test_convert__endianness_degC_to_kelvin(unittest.TestCase):
    # Test the behaviour of converting temperature units of differing
    # dtype endianness.

    def setUp(self):
        self.k_array = np.array([356.7, 356.8, 356.9])
        self.degc_array = np.array([83.55, 83.65, 83.75])
        self.degc = cf_units.Unit("degC")
        self.k = cf_units.Unit("K")

    def test_no_endian(self):
        dtype = "f8"
        result = self.degc.convert(self.degc_array.astype(dtype), self.k)
        np.testing.assert_array_almost_equal(result, self.k_array)

    def test_little_endian(self):
        dtype = "<f8"
        result = self.degc.convert(self.degc_array.astype(dtype), self.k)
        np.testing.assert_array_almost_equal(result, self.k_array)

    def test_big_endian(self):
        dtype = ">f8"
        result = self.degc.convert(self.degc_array.astype(dtype), self.k)
        np.testing.assert_array_almost_equal(result, self.k_array)


class Test_convert__result_ctype(unittest.TestCase):
    # Test the output ctype of converting an cf_unit.

    def setUp(self):
        self.initial_dtype = np.float32
        self.degs_array = np.array(
            [356.7, 356.8, 356.9], dtype=self.initial_dtype
        )
        self.deg = cf_units.Unit("degrees")
        self.rad = cf_units.Unit("radians")

    def test_default(self):
        # The dtype of a float array should be unchanged.
        result = self.deg.convert(self.degs_array, self.rad)
        self.assertEqual(result.dtype, self.initial_dtype)

    def test_integer_ctype_default(self):
        # The ctype of an int array should be cast to the default ctype.
        result = self.deg.convert(self.degs_array.astype(np.int32), self.rad)
        self.assertEqual(result.dtype, cf_units.FLOAT64)

    def test_integer_ctype_specified(self):
        # The ctype of an int array should be cast to the specified ctype if
        # supplied.
        expected_dtype = cf_units.FLOAT32
        result = self.deg.convert(
            self.degs_array.astype(np.int32), self.rad, ctype=expected_dtype
        )
        self.assertEqual(result.dtype, expected_dtype)


class Test_convert__masked_array(unittest.TestCase):
    # Test converting an cf_unit with masked data.

    def setUp(self):
        self.deg = cf_units.Unit("degrees")
        self.rad = cf_units.Unit("radians")
        self.degs_array = np.ma.array(
            np.array([356.7, 356.8, 356.9], dtype=np.float32),
            mask=np.array([0, 1, 0], dtype=bool),
        )
        self.rads_array = np.ma.array(
            np.array([6.22558944, 6.22733477, 6.2290801], dtype=np.float32),
            mask=np.array([0, 1, 0], dtype=bool),
        )

    def test_no_type_conversion(self):
        result = self.deg.convert(
            self.degs_array, self.rad, ctype=cf_units.FLOAT32
        )
        np.testing.assert_array_almost_equal(self.rads_array, result)

    def test_type_conversion(self):
        result = self.deg.convert(
            self.degs_array, self.rad, ctype=cf_units.FLOAT64
        )
        np.testing.assert_array_almost_equal(self.rads_array, result)


class Test_is_long_time_interval(unittest.TestCase):
    def test_short_time_interval(self):
        # A short time interval is a time interval from seconds to days.
        unit = Unit("seconds since epoch")
        result = unit.is_long_time_interval()
        self.assertFalse(result)

    def test_long_time_interval(self):
        # A long time interval is a time interval of months or years.
        unit = Unit("months since epoch")
        result = unit.is_long_time_interval()
        self.assertTrue(result)

    def test_calendar(self):
        # Check that a different calendar does not affect the result.
        unit = Unit("months since epoch", calendar=cf_units.CALENDAR_360_DAY)
        result = unit.is_long_time_interval()
        self.assertTrue(result)

    def test_not_time_unit(self):
        unit = Unit("K")
        result = unit.is_long_time_interval()
        self.assertFalse(result)


class Test_format(unittest.TestCase):
    def test_invalid_ut_unit(self):
        # https://github.com/SciTools/cf-units/issues/133 flagged up that
        # format should be a little more tolerant of a Unit that has not been
        # constructed correctly when using pytest.
        unit = Unit.__new__(Unit)
        self.assertEqual(unit.format(), "unknown")


if __name__ == "__main__":
    unittest.main()
