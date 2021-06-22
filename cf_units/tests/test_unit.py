# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
Test Unit the wrapper class for Unidata udunits2.

"""

import copy
import datetime as datetime
import operator
import re
import unittest
from operator import truediv

import cftime
import numpy as np

import cf_units as unit
from cf_units import suppress_errors

Unit = unit.Unit


class Test_unit__creation(unittest.TestCase):
    def test_is_valid_unit_string(self):
        unit_strs = ["    meter", "meter    ", "    meter   "]
        for unit_str in unit_strs:
            u = Unit(unit_str)
            self.assertEqual(u.name, "meter")

    def test_not_valid_unit_str(self):
        with self.assertRaisesRegex(ValueError, "Failed to parse unit"):
            Unit("wibble")

    def test_calendar(self):
        calendar = unit.CALENDAR_365_DAY
        u = Unit("hours since 1970-01-01 00:00:00", calendar=calendar)
        self.assertEqual(u.calendar, calendar)

    def test_calendar_alias(self):
        calendar = unit.CALENDAR_NO_LEAP
        u = Unit("hours since 1970-01-01 00:00:00", calendar=calendar)
        self.assertEqual(u.calendar, unit.CALENDAR_365_DAY)

    def test_no_calendar(self):
        u = Unit("hours since 1970-01-01 00:00:00")
        self.assertEqual(u.calendar, unit.CALENDAR_GREGORIAN)

    def test_unsupported_calendar(self):
        with self.assertRaisesRegex(ValueError, "unsupported calendar"):
            Unit("hours since 1970-01-01 00:00:00", calendar="wibble")

    def test_calendar_w_unicode(self):
        calendar = unit.CALENDAR_365_DAY
        u = Unit("hours\xb2 hours-1 since epoch", calendar=calendar)
        self.assertEqual(u.calendar, calendar)
        expected = "hours² hours-1 since 1970-01-01 00:00:00"
        self.assertEqual(u.origin, expected)

    def test_unicode_valid(self):
        # Some unicode characters are allowed.
        u = Unit("m²")
        assert u.symbol == "m2"

    def test_py2k_unicode(self):
        u = Unit("m\xb2")
        assert u.symbol == "m2"

    def test_unicode_invalid(self):
        # Not all unicode characters are allowed.
        msg = r"Failed to parse unit \"ø\""
        with self.assertRaisesRegex(ValueError, msg):
            Unit("ø")


class Test_modulus(unittest.TestCase):
    def test_modulus__degrees(self):
        u = Unit("degrees")
        self.assertEqual(u.modulus, 360.0)

    def test_modulus__radians(self):
        u = Unit("radians")
        self.assertEqual(u.modulus, np.pi * 2)

    def test_no_modulus(self):
        u = Unit("meter")
        self.assertEqual(u.modulus, None)


class Test_is_convertible(unittest.TestCase):
    def test_convert_distance_to_force(self):
        u = Unit("meter")
        v = Unit("newton")
        self.assertFalse(u.is_convertible(v))

    def test_convert_distance_units(self):
        u = Unit("meter")
        v = Unit("mile")
        self.assertTrue(u.is_convertible(v))

    def test_convert_to_unknown(self):
        u = Unit("meter")
        v = Unit("unknown")
        self.assertFalse(u.is_convertible(v))
        self.assertFalse(v.is_convertible(u))

    def test_convert_to_no_unit(self):
        u = Unit("meter")
        v = Unit("no unit")
        self.assertFalse(u.is_convertible(v))
        self.assertFalse(v.is_convertible(u))

    def test_convert_unknown_to_no_unit(self):
        u = Unit("unknown")
        v = Unit("no unit")
        self.assertFalse(u.is_convertible(v))
        self.assertFalse(v.is_convertible(u))


class Test_is_dimensionless(unittest.TestCase):
    def test_dimensionless(self):
        u = Unit("1")
        self.assertTrue(u.is_dimensionless())

    def test_distance_dimensionless(self):
        u = Unit("meter")
        self.assertFalse(u.is_dimensionless())

    def test_unknown_dimensionless(self):
        u = Unit("unknown")
        self.assertFalse(u.is_dimensionless())

    def test_no_unit_dimensionless(self):
        u = Unit("no unit")
        self.assertFalse(u.is_dimensionless())


class Test_format(unittest.TestCase):
    def test_basic(self):
        u = Unit("watt")
        self.assertEqual(u.format(), "W")

    def test_format_ascii(self):
        u = Unit("watt")
        self.assertEqual(u.format(unit.UT_ASCII), "W")

    def test_format_ut_names(self):
        u = Unit("watt")
        self.assertEqual(u.format(unit.UT_NAMES), "watt")

    def test_format_unit_definition(self):
        u = Unit("watt")
        self.assertEqual(u.format(unit.UT_DEFINITION), "m2.kg.s-3")

    def test_format_multiple_options(self):
        u = Unit("watt")
        self.assertEqual(
            u.format([unit.UT_NAMES, unit.UT_DEFINITION]),
            "meter^2-kilogram-second^-3",
        )

    def test_format_multiple_options_utf8(self):
        u = Unit("watt")
        self.assertEqual(
            u.format([unit.UT_NAMES, unit.UT_DEFINITION, unit.UT_UTF8]),
            "meter²·kilogram·second⁻³",
        )

    def test_format_unknown(self):
        u = Unit("?")
        self.assertEqual(u.format(), "unknown")

    def test_format_no_unit(self):
        u = Unit("nounit")
        self.assertEqual(u.format(), "no_unit")

    def test_format_names_utf8(self):
        u = Unit("m2")
        self.assertEqual(u.format([unit.UT_UTF8, unit.UT_NAMES]), "meter²")

    def test_format_latin1(self):
        u = Unit("m2")
        self.assertEqual(u.format(unit.UT_LATIN1), "m²")


class Test_name(unittest.TestCase):
    def test_basic(self):
        u = Unit("newton")
        self.assertEqual(u.name, "newton")

    def test_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u.name, "unknown")

    def test_no_unit(self):
        u = Unit("no unit")
        self.assertEqual(u.name, "no_unit")


class Test_symbol(unittest.TestCase):
    def test_basic(self):
        u = Unit("joule")
        self.assertEqual(u.symbol, "J")

    def test_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u.symbol, unit._UNKNOWN_UNIT_SYMBOL)

    def test_no_unit(self):
        u = Unit("no unit")
        self.assertEqual(u.symbol, unit._NO_UNIT_SYMBOL)


class Test_definition(unittest.TestCase):
    def test_basic(self):
        u = Unit("joule")
        self.assertEqual(u.definition, "m2.kg.s-2")

    def test_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u.definition, unit._UNKNOWN_UNIT_SYMBOL)

    def test_no_unit(self):
        u = Unit("no unit")
        self.assertEqual(u.definition, unit._NO_UNIT_SYMBOL)


class Test__apply_offset(unittest.TestCase):
    def test_add_integer_offset(self):
        u = Unit("meter")
        self.assertEqual(u + 10, "m @ 10")

    def test_add_float_offset(self):
        u = Unit("meter")
        self.assertEqual(u + 100.0, "m @ 100")

    def test_not_numerical_offset(self):
        u = Unit("meter")
        with self.assertRaisesRegex(TypeError, "unsupported operand type"):
            operator.add(u, "not_a_number")

    def test_unit_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u + 10, "unknown")

    def test_no_unit(self):
        u = Unit("no unit")
        with self.assertRaisesRegex(ValueError, "Cannot offset"):
            operator.add(u, 10)


class Test_offset_by_time(unittest.TestCase):
    def test_offset(self):
        u = Unit("hour")
        v = u.offset_by_time(unit.encode_time(2007, 1, 15, 12, 6, 0))
        self.assertEqual(v, "(3600 s) @ 20070115T120600.00000000 UTC")

    def test_not_numerical_offset(self):
        u = Unit("hour")
        with self.assertRaisesRegex(TypeError, "numeric type"):
            u.offset_by_time("not_a_number")

    def test_not_time_unit(self):
        u = Unit("mile")
        with self.assertRaisesRegex(ValueError, "Failed to offset"):
            u.offset_by_time(10)

    def test_unit_unknown(self):
        u = Unit("unknown")
        emsg = "Failed to offset"
        with self.assertRaisesRegex(ValueError, emsg), suppress_errors():
            u.offset_by_time(unit.encode_time(1970, 1, 1, 0, 0, 0))

    def test_no_unit(self):
        u = Unit("no unit")
        emsg = "Failed to offset"
        with self.assertRaisesRegex(ValueError, emsg), suppress_errors():
            u.offset_by_time(unit.encode_time(1970, 1, 1, 0, 0, 0))


class Test_invert(unittest.TestCase):
    def test_basic(self):
        u = Unit("newton")
        self.assertEqual(u.invert(), "m-1.kg-1.s2")

    def test_double_invert(self):
        # Double-inverting a unit should take you back to where you started.
        u = Unit("newton")
        self.assertEqual(u.invert().invert(), u)

    def test_invert_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u.invert(), u)

    def test_invert_no_unit(self):
        u = Unit("no unit")
        with self.assertRaisesRegex(ValueError, "Cannot invert"):
            u.invert()


class Test_root(unittest.TestCase):
    def setUp(self):
        unit.suppress_errors()

    def test_square_root(self):
        u = Unit("volt^2")
        self.assertEqual(u.root(2), "V")

    def test_square_root_integer_float(self):
        u = Unit("volt^2")
        self.assertEqual(u.root(2.0), "V")

    def test_not_numeric(self):
        u = Unit("volt")
        with self.assertRaisesRegex(TypeError, "numeric type"):
            u.offset_by_time("not_a_number")

    def test_not_integer(self):
        u = Unit("volt")
        with self.assertRaisesRegex(TypeError, "integer .* required"):
            u.root(1.2)

    def test_meaningless_operation(self):
        u = Unit("volt")
        emsg = "UT_MEANINGLESS"
        with self.assertRaisesRegex(ValueError, emsg), suppress_errors():
            u.root(2)

    def test_unit_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u.root(2), u)

    def test_no_unit(self):
        u = Unit("no unit")
        with self.assertRaisesRegex(ValueError, "Cannot take the root"):
            u.root(2)


class Test_log(unittest.TestCase):
    def test_base_2(self):
        u = Unit("hPa")
        self.assertEqual(u.log(2), "lb(re 100 Pa)")

    def test_base_10(self):
        u = Unit("hPa")
        self.assertEqual(u.log(10), "lg(re 100 Pa)")

    def test_negative(self):
        u = Unit("hPa")
        msg = re.escape("Failed to calculate logorithmic base of Unit('hPa')")
        with self.assertRaisesRegex(ValueError, msg):
            u.log(-1)

    def test_not_numeric(self):
        u = Unit("hPa")
        with self.assertRaisesRegex(TypeError, "numeric type"):
            u.log("not_a_number")

    def test_unit_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u.log(10), u)

    def test_no_unit(self):
        u = Unit("no unit")
        emsg = "Cannot take the logarithm"
        with self.assertRaisesRegex(ValueError, emsg):
            u.log(10)


class Test_multiply(unittest.TestCase):
    def test_multiply_by_int(self):
        u = Unit("amp")
        self.assertEqual((u * 10).format(), "10 A")

    def test_multiply_by_float(self):
        u = Unit("amp")
        self.assertEqual((u * 100.0).format(), "100 A")

    def test_multiply_electrical_units(self):
        u = Unit("amp")
        v = Unit("volt")
        self.assertEqual((u * v).format(), "W")

    def test_multiply_not_numeric(self):
        u = Unit("amp")
        with self.assertRaisesRegex(ValueError, "Failed to parse unit"):
            operator.mul(u, "not_a_number")

    def test_multiply_with_unknown_unit(self):
        u = Unit("unknown")
        v = Unit("meters")
        self.assertTrue((u * v).is_unknown())
        self.assertTrue((v * u).is_unknown())

    def test_multiply_with_no_unit(self):
        u = Unit("meters")
        v = Unit("no unit")
        with self.assertRaisesRegex(ValueError, "Cannot multiply"):
            operator.mul(u, v)
            operator.mul(v, u)

    def test_multiply_unknown_and_no_unit(self):
        u = Unit("unknown")
        v = Unit("no unit")
        with self.assertRaisesRegex(ValueError, "Cannot multiply"):
            operator.mul(u, v)
            operator.mul(v, u)


class Test_divide(unittest.TestCase):
    def test_divide_by_int(self):
        u = Unit("watts")
        self.assertEqual((u / 10).format(), "0.1 W")

    def test_divide_by_float(self):
        u = Unit("watts")
        self.assertEqual((u / 100.0).format(), "0.01 W")

    def test_divide_electrical_units(self):
        u = Unit("watts")
        v = Unit("volts")
        self.assertEqual((u / v).format(), "A")

    def test_divide_not_numeric(self):
        u = Unit("watts")
        with self.assertRaisesRegex(ValueError, "Failed to parse unit"):
            truediv(u, "not_a_number")

    def test_divide_with_unknown_unit(self):
        u = Unit("unknown")
        v = Unit("meters")
        self.assertTrue((u / v).is_unknown())
        self.assertTrue((v / u).is_unknown())

    def test_divide_with_no_unit(self):
        u = Unit("meters")
        v = Unit("no unit")
        with self.assertRaisesRegex(ValueError, "Cannot divide"):
            truediv(u, v)
            truediv(v, u)

    def test_divide_unknown_and_no_unit(self):
        u = Unit("unknown")
        v = Unit("no unit")
        with self.assertRaisesRegex(ValueError, "Cannot divide"):
            truediv(u, v)
            truediv(v, u)


class Test_power(unittest.TestCase):
    def test_basic(self):
        u = Unit("m^2")
        self.assertEqual(u ** 0.5, Unit("m"))

    def test_integer_power(self):
        u = Unit("amp")
        self.assertEqual(u ** 2, Unit("A^2"))

    def test_float_power(self):
        u = Unit("amp")
        self.assertEqual(u ** 3.0, Unit("A^3"))

    def test_dimensionless(self):
        u = Unit("1")
        self.assertEqual(u ** 2, u)

    def test_power(self):
        u = Unit("amp")
        self.assertRaises(TypeError, operator.pow, u, Unit("m"))
        self.assertRaises(TypeError, operator.pow, u, Unit("unknown"))
        self.assertRaises(TypeError, operator.pow, u, Unit("no unit"))

    def test_not_numeric(self):
        u = Unit("m^2")
        emsg = "numeric value is required"
        with self.assertRaisesRegex(TypeError, emsg):
            operator.pow(u, "not_a_number")

    def test_bad_power(self):
        u = Unit("m^2")
        emsg = "Cannot raise .* by a decimal"
        with self.assertRaisesRegex(ValueError, emsg):
            operator.pow(u, 0.4)

    def test_unit_power(self):
        u = Unit("amp")
        v = Unit("m")
        emsg = "argument must be a string or a number"
        with self.assertRaisesRegex(TypeError, emsg):
            operator.pow(u, v)


class Test_power__unknown(unittest.TestCase):
    def setUp(self):
        self.u = Unit("unknown")

    def test_integer_power(self):
        self.assertEqual(self.u ** 2, Unit("unknown"))

    def test_float_power(self):
        self.assertEqual(self.u ** 3.0, Unit("unknown"))

    def test_not_numeric(self):
        emsg = "numeric value is required"
        with self.assertRaisesRegex(TypeError, emsg):
            operator.pow(self.u, "not_a_number")

    def test_bad_power(self):
        self.assertEqual(self.u ** 0.4, self.u)

    def test_unit_power(self):
        v = Unit("m")
        emsg = "argument must be a string or a number"
        with self.assertRaisesRegex(TypeError, emsg):
            operator.pow(self.u, v)


class Test_power__no_unit(unittest.TestCase):
    def setUp(self):
        self.u = Unit("no unit")

    def test_integer_power(self):
        emsg = "Cannot raise .* a 'no-unit'"
        with self.assertRaisesRegex(ValueError, emsg):
            operator.pow(self.u, 2)

    def test_float_power(self):
        emsg = "Cannot raise .* a 'no-unit'"
        with self.assertRaisesRegex(ValueError, emsg):
            operator.pow(self.u, 3.0)

    def test_not_numeric(self):
        emsg = "numeric value is required"
        with self.assertRaisesRegex(TypeError, emsg):
            operator.pow(self.u, "not_a_number")

    def test_bad_power(self):
        emsg = "Cannot raise .* a 'no-unit'"
        with self.assertRaisesRegex(ValueError, emsg):
            operator.pow(self.u, 0.4)

    def test_unit_power(self):
        v = Unit("m")
        emsg = "argument must be a string or a number"
        with self.assertRaisesRegex(TypeError, emsg):
            operator.pow(self.u, v)


class Test_copy(unittest.TestCase):
    def test_basic(self):
        u = Unit("joule")
        self.assertEqual(copy.copy(u), u)

    def test_unit_unknown(self):
        u = Unit("unknown")
        self.assertEqual(copy.copy(u), u)
        self.assertTrue(copy.copy(u).is_unknown())

    def test_no_unit(self):
        u = Unit("no unit")
        self.assertEqual(copy.copy(u), u)
        self.assertTrue(copy.copy(u).is_no_unit())


class Test_stringify(unittest.TestCase):
    def test___str__(self):
        u = Unit("meter")
        self.assertEqual(str(u), "meter")

    def test___repr___basic(self):
        u = Unit("meter")
        self.assertEqual(repr(u), "Unit('meter')")

    def test___repr___time_unit(self):
        u = Unit(
            "hours since 2007-01-15 12:06:00", calendar=unit.CALENDAR_STANDARD
        )
        exp = "Unit('hours since 2007-01-15 12:06:00', calendar='gregorian')"
        self.assertEqual(repr(u), exp)


class Test_equality(unittest.TestCase):
    def test_basic(self):
        u = Unit("meter")
        self.assertEqual(u, "meter")

    def test_equivalent_units(self):
        u = Unit("meter")
        v = Unit("m.s-1")
        w = Unit("hertz")
        self.assertEqual(u, v / w)

    def test_non_equivalent_units(self):
        u = Unit("meter")
        v = Unit("amp")
        self.assertNotEqual(u, v)

    def test_eq_cross_category(self):
        m = Unit("meter")
        u = Unit("unknown")
        n = Unit("no_unit")
        self.assertNotEqual(m, u)
        self.assertNotEqual(m, n)

    def test_unknown(self):
        u = Unit("unknown")
        self.assertEqual(u, "unknown")

    def test_no_unit(self):
        u = Unit("no_unit")
        self.assertEqual(u, "no_unit")

    def test_unknown_no_unit(self):
        u = Unit("unknown")
        v = Unit("no_unit")
        self.assertNotEqual(u, v)

    def test_not_implemented(self):
        u = Unit("meter")
        self.assertFalse(u == {})


class Test_non_equality(unittest.TestCase):
    def test_basic(self):
        u = Unit("meter")
        self.assertFalse(u != "meter")

    def test_non_equivalent_units(self):
        u = Unit("meter")
        v = Unit("amp")
        self.assertNotEqual(u, v)

    def test_ne_cross_category(self):
        m = Unit("meter")
        u = Unit("unknown")
        n = Unit("no_unit")
        self.assertNotEqual(m, u)
        self.assertNotEqual(m, n)
        self.assertNotEqual(u, n)

    def test_unknown(self):
        u = Unit("unknown")
        self.assertFalse(u != "unknown")

    def test_no_unit(self):
        u = Unit("no_unit")
        self.assertFalse(u != "no_unit")

    def test_not_implemented(self):
        u = Unit("meter")
        self.assertNotEqual(u, {})


class Test_convert(unittest.TestCase):
    def test_convert_float(self):
        u = Unit("meter")
        v = Unit("mile")
        result = u.convert(1609.344, v)
        expected = 1.0
        self.assertEqual(result, expected)

    def test_convert_int(self):
        u = Unit("mile")
        v = Unit("meter")
        result = u.convert(1, v)
        expected = 1609.344
        self.assertEqual(result, expected)

    def test_convert_array(self):
        u = Unit("meter")
        v = Unit("mile")
        expected = np.arange(2, dtype=np.float32) + 1
        result = u.convert(expected * 1609.344, v)
        np.testing.assert_array_equal(result, expected)

    def test_convert_array_multidim(self):
        u = Unit("meter")
        v = Unit("mile")
        expected = (np.arange(2, dtype=np.float32) + 1).reshape([1, 1, 2, 1])
        result = u.convert(expected * 1609.344, v)
        np.testing.assert_array_equal(result, expected)

    def test_incompatible_units(self):
        u = Unit("m")
        v = Unit("V")
        emsg = "Unable to convert"
        with self.assertRaisesRegex(ValueError, emsg):
            u.convert(1.0, v)

    def test_unknown_units(self):
        u = Unit("unknown")
        v = Unit("no unit")
        m = Unit("m")
        val = 1.0
        emsg = "Unable to convert"
        with self.assertRaisesRegex(ValueError, emsg):
            u.convert(val, m)
        with self.assertRaisesRegex(ValueError, emsg):
            m.convert(val, u)
        with self.assertRaisesRegex(ValueError, emsg):
            u.convert(val, v)

    def test_no_units(self):
        u = Unit("no unit")
        v = Unit("unknown")
        m = Unit("m")
        val = 1.0
        emsg = "Unable to convert"
        with self.assertRaisesRegex(ValueError, emsg):
            u.convert(val, m)
        with self.assertRaisesRegex(ValueError, emsg):
            m.convert(val, u)
        with self.assertRaisesRegex(ValueError, emsg):
            u.convert(val, v)

    def test_convert_time_units(self):
        u = Unit("seconds since 1978-09-01 00:00:00", calendar="360_day")
        v = Unit("seconds since 1979-04-01 00:00:00", calendar="360_day")
        u1point = np.array([54432000.0], dtype=np.float32)
        u2point = np.array([36288000.0], dtype=np.float32)
        res = u.convert(u1point, v)
        np.testing.assert_array_almost_equal(res, u2point, decimal=6)

    def test_incompatible_time_units(self):
        u = Unit("seconds since 1978-09-01 00:00:00", calendar="360_day")
        v = Unit("seconds since 1979-04-01 00:00:00", calendar="gregorian")
        u1point = np.array([54432000.0], dtype=np.float32)
        emsg = "Unable to convert"
        with self.assertRaisesRegex(ValueError, emsg):
            u.convert(u1point, v)


class Test_order(unittest.TestCase):
    def test(self):
        m = Unit("meter")
        u = Unit("unknown")
        n = Unit("no_unit")
        start = [m, u, n]
        self.assertEqual(sorted(start), [m, n, u])


class Test_is_unknown(unittest.TestCase):
    def _check(self, unknown_str):
        u = Unit(unknown_str)
        self.assertTrue(u.is_unknown())

    def test_unknown_representations(self):
        representations = ["unknown", "?", "???"]
        for representation in representations:
            self._check(representation)

    def test_no_unit(self):
        u = Unit("no unit")
        self.assertFalse(u.is_unknown())

    def test_known_unit(self):
        u = Unit("meters")
        self.assertFalse(u.is_unknown())

    def test_no_ut_pointer(self):
        # Test that a unit that was poorly constructed has a
        # degree of tolerance by making it unknown.
        # https://github.com/SciTools/cf-units/issues/133 refers.
        self.assertTrue(Unit.__new__(Unit).is_unknown())


class Test_is_no_unit(unittest.TestCase):
    def _check(self, no_unit_str):
        u = Unit(no_unit_str)
        self.assertTrue(u.is_no_unit())

    def test_no_unit_representations(self):
        representations = ["no_unit", "no unit", "no-unit", "nounit"]
        for representation in representations:
            self._check(representation)

    def test_unknown(self):
        u = Unit("unknown")
        self.assertFalse(u.is_no_unit())

    def test_known_unit(self):
        u = Unit("meters")
        self.assertFalse(u.is_no_unit())


class Test_is_udunits(unittest.TestCase):
    def test_basic(self):
        u = Unit("meters")
        self.assertTrue(u.is_udunits())

    def test_unknown(self):
        u = Unit("unknown")
        self.assertFalse(u.is_udunits())

    def test_no_unit(self):
        u = Unit("no_unit")
        self.assertFalse(u.is_udunits())


class Test_is_time_reference(unittest.TestCase):
    def test_basic(self):
        u = Unit("hours since epoch")
        self.assertTrue(u.is_time_reference())

    def test_not_time_reference(self):
        u = Unit("hours")
        self.assertFalse(u.is_time_reference())

    def test_unknown(self):
        u = Unit("unknown")
        self.assertFalse(u.is_time_reference())

    def test_no_unit(self):
        u = Unit("no_unit")
        self.assertFalse(u.is_time_reference())


class Test_title(unittest.TestCase):
    def test_basic(self):
        u = Unit("meter")
        self.assertEqual(u.title(10), "10 meter")

    def test_time_unit(self):
        u = Unit("hours since epoch", calendar=unit.CALENDAR_STANDARD)
        self.assertEqual(u.title(10), "1970-01-01 10:00:00")


class Test__immutable(unittest.TestCase):
    def _set_attr(self, unit, name):
        setattr(unit, name, -999)
        raise ValueError("'Unit' attribute {!r} is mutable!".format(name))

    def test_immutable(self):
        u = Unit("m")
        for name in dir(u):
            emsg = "Instances .* are immutable"
            with self.assertRaisesRegex(AttributeError, emsg):
                self._set_attr(u, name)

    def test_common_hash(self):
        # Test different instances of length units (m) have a common hash.
        u1 = Unit("m")
        u2 = Unit("meter")
        u3 = copy.deepcopy(u1)
        h = set()
        for u in (u1, u2, u3):
            h.add(hash(u))
        self.assertEqual(len(h), 1)

        # Test different instances of electrical units (V) have a common hash.
        v1 = Unit("V")
        v2 = Unit("volt")
        for u in (v1, v2):
            h.add(hash(u))
        self.assertEqual(len(h), 2)


class Test__inplace(unittest.TestCase):
    # Test shared memory for conversion operations.

    def test(self):
        # Check conversions do not change original object.
        c = Unit("deg_c")
        f = Unit("deg_f")

        orig = np.arange(3, dtype=np.float32)

        # Test arrays are not equal without inplace conversions.
        converted = c.convert(orig, f)

        emsg = "Arrays are not equal"
        with self.assertRaisesRegex(AssertionError, emsg):
            np.testing.assert_array_equal(orig, converted)
        self.assertFalse(np.may_share_memory(orig, converted))

        # Test inplace conversion alters the original array.
        converted = c.convert(orig, f, inplace=True)
        np.testing.assert_array_equal(orig, converted)
        self.assertTrue(np.may_share_memory(orig, converted))

    def test_multidim_masked(self):
        c = Unit("deg_c")
        f = Unit("deg_f")

        # Manufacture a Fortran-ordered nd array to be converted.
        orig = (
            np.ma.masked_array(
                np.arange(4, dtype=np.float32), mask=[1, 0, 0, 1]
            )
            .reshape([2, 2])
            .T
        )

        # Test arrays are not equal without inplace conversions.
        converted = c.convert(orig, f)

        emsg = "Arrays are not equal"
        with self.assertRaisesRegex(AssertionError, emsg):
            np.testing.assert_array_equal(orig.data, converted.data)
        self.assertFalse(np.may_share_memory(orig, converted))

        # Test inplace conversion alters the original array.
        converted = c.convert(orig, f, inplace=True)
        np.testing.assert_array_equal(orig.data, converted.data)
        self.assertTrue(np.may_share_memory(orig, converted))

    def test_foreign_endian(self):
        c = Unit("deg_c")
        f = Unit("deg_f")

        # Manufacture a non-native byte-order array to be converted.
        orig = np.arange(4, dtype=np.float32).newbyteorder().byteswap()

        emsg = (
            "Unable to convert non-native byte ordered array in-place. "
            "Consider byte-swapping first."
        )
        with self.assertRaisesRegex(ValueError, emsg):
            c.convert(orig, f, inplace=True)

        # Test we can do this when not-inplace
        c.convert(orig, f)


class TestTimeEncoding(unittest.TestCase):
    def test_encode_time(self):
        result = unit.encode_time(2006, 1, 15, 12, 6, 0)
        self.assertEqual(result, 159019560.0)

    def test_encode_date(self):
        result = unit.encode_date(2006, 1, 15)
        self.assertEqual(result, 158976000.0)

    def test_encode_clock(self):
        result = unit.encode_clock(12, 6, 0)
        self.assertEqual(result, 43560.0)

    def test_decode_time(self):
        result = unit.decode_time(158976000.0 + 43560.0)
        year, month, day, hour, min, sec, res = result
        self.assertEqual(
            (year, month, day, hour, min, sec), (2006, 1, 15, 12, 6, 0)
        )


class TestNumsAndDates(unittest.TestCase):
    def test_num2date(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00", calendar=unit.CALENDAR_STANDARD
        )
        res = u.num2date(1)
        self.assertEqual(str(res), "2010-11-02 13:00:00")
        self.assertEqual(res.calendar, "gregorian")
        self.assertIsInstance(res, cftime.datetime)

    def test_num2date_py_datetime_type(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00", calendar=unit.CALENDAR_STANDARD
        )
        res = u.num2date(1, only_use_cftime_datetimes=False)
        self.assertEqual(str(res), "2010-11-02 13:00:00")
        self.assertIsInstance(res, datetime.datetime)

    def test_num2date_wrong_calendar(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00", calendar=unit.CALENDAR_360_DAY
        )
        with self.assertRaisesRegex(
            ValueError, "illegal calendar or reference date"
        ):
            u.num2date(
                1,
                only_use_cftime_datetimes=False,
                only_use_python_datetimes=True,
            )

    def test_date2num(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00", calendar=unit.CALENDAR_STANDARD
        )
        d = datetime.datetime(2010, 11, 2, 13, 0, 0)
        self.assertEqual(str(u.num2date(u.date2num(d))), "2010-11-02 13:00:00")

    def test_num2pydate_simple(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00", calendar=unit.CALENDAR_STANDARD
        )
        result = u.num2pydate(1)
        expected = datetime.datetime(2010, 11, 2, 13)
        self.assertEqual(result, expected)
        self.assertIsInstance(result, datetime.datetime)

    def test_num2pydate_wrong_calendar(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00", calendar=unit.CALENDAR_360_DAY
        )
        with self.assertRaisesRegex(
            ValueError, "illegal calendar or reference date"
        ):
            u.num2pydate(1)


class Test_as_unit(unittest.TestCase):
    def test_already_unit(self):
        u = Unit("m")
        result = unit.as_unit(u)
        self.assertIs(result, u)

    def test_known_unit_str(self):
        u_str = "m"
        expected = Unit("m")
        result = unit.as_unit(u_str)
        self.assertEqual(expected, result)

    def test_not_unit_str(self):
        u_str = "wibble"
        emsg = "Failed to parse unit"
        with self.assertRaisesRegex(ValueError, emsg):
            unit.as_unit(u_str)

    def test_unknown_str(self):
        u_str = "unknown"
        expected = Unit("unknown")
        result = unit.as_unit(u_str)
        self.assertEqual(expected, result)

    def test_no_unit_str(self):
        u_str = "no_unit"
        expected = Unit("no_unit")
        result = unit.as_unit(u_str)
        self.assertEqual(expected, result)


class Test_is_time(unittest.TestCase):
    def test_basic(self):
        u = Unit("hours")
        self.assertTrue(u.is_time())

    def test_not_time_unit(self):
        u = Unit("meters")
        self.assertFalse(u.is_time())

    def test_unknown(self):
        u = Unit("unknown")
        self.assertFalse(u.is_time())

    def test_no_unit(self):
        u = Unit("no_unit")
        self.assertFalse(u.is_time())


class Test_is_vertical(unittest.TestCase):
    def test_pressure_unit(self):
        u = Unit("millibar")
        self.assertTrue(u.is_vertical())

    def test_length_unit(self):
        u = Unit("meters")
        self.assertTrue(u.is_vertical())

    def test_not_vertical_unit(self):
        u = Unit("hours")
        self.assertFalse(u.is_vertical())

    def test_unknown(self):
        u = Unit("unknown")
        self.assertFalse(u.is_vertical())

    def test_no_unit(self):
        u = Unit("no_unit")
        self.assertFalse(u.is_vertical())


if __name__ == "__main__":
    unittest.main()
