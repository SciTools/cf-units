# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""Test Unit the wrapper class for Unidata udunits2."""

import copy
import datetime as datetime
import operator
import re
from operator import truediv

import cftime
import numpy as np
import pytest

import cf_units
from cf_units import suppress_errors

Unit = cf_units.Unit


class Test_unit__creation:
    def test_is_valid_unit_string(self):
        unit_strs = ["    meter", "meter    ", "    meter   "]
        for unit_str in unit_strs:
            u = Unit(unit_str)
            assert u.name == "meter"

    def test_not_valid_unit_str(self):
        with pytest.raises(ValueError, match="Failed to parse unit"):
            Unit("wibble")

    def test_calendar(self):
        calendar = cf_units.CALENDAR_365_DAY
        u = Unit("hours since 1970-01-01 00:00:00", calendar=calendar)
        assert u.calendar == calendar

    def test_calendar_alias(self):
        calendar = cf_units.CALENDAR_NO_LEAP
        u = Unit("hours since 1970-01-01 00:00:00", calendar=calendar)
        assert u.calendar == cf_units.CALENDAR_365_DAY

    def test_no_calendar(self):
        u = Unit("hours since 1970-01-01 00:00:00")
        assert u.calendar == cf_units.CALENDAR_STANDARD

    def test_unsupported_calendar(self):
        with pytest.raises(ValueError, match="unsupported calendar"):
            Unit("hours since 1970-01-01 00:00:00", calendar="wibble")

    def test_calendar_w_unicode(self):
        calendar = cf_units.CALENDAR_365_DAY
        u = Unit("hours\xb2 hours-1 since epoch", calendar=calendar)
        assert u.calendar == calendar
        expected = "hours² hours-1 since 1970-01-01 00:00:00"
        assert u.origin == expected

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
        with pytest.raises(ValueError, match=msg):
            Unit("ø")


class Test_modulus:
    def test_modulus__degrees(self):
        u = Unit("degrees")
        assert u.modulus == 360.0

    def test_modulus__radians(self):
        u = Unit("radians")
        assert u.modulus == np.pi * 2

    def test_no_modulus(self):
        u = Unit("meter")
        assert u.modulus is None


class Test_is_convertible:
    def test_convert_distance_to_force(self):
        u = Unit("meter")
        v = Unit("newton")
        assert not u.is_convertible(v)

    def test_convert_distance_units(self):
        u = Unit("meter")
        v = Unit("mile")
        assert u.is_convertible(v)

    def test_convert_to_unknown(self):
        u = Unit("meter")
        v = Unit("unknown")
        assert not u.is_convertible(v)
        assert not v.is_convertible(u)

    def test_convert_to_no_unit(self):
        u = Unit("meter")
        v = Unit("no unit")
        assert not u.is_convertible(v)
        assert not v.is_convertible(u)

    def test_convert_unknown_to_no_unit(self):
        u = Unit("unknown")
        v = Unit("no unit")
        assert not u.is_convertible(v)
        assert not v.is_convertible(u)


class Test_is_dimensionless:
    def test_dimensionless(self):
        u = Unit("1")
        assert u.is_dimensionless()

    def test_distance_dimensionless(self):
        u = Unit("meter")
        assert not u.is_dimensionless()

    def test_unknown_dimensionless(self):
        u = Unit("unknown")
        assert not u.is_dimensionless()

    def test_no_unit_dimensionless(self):
        u = Unit("no unit")
        assert not u.is_dimensionless()


class Test_format:
    def test_basic(self):
        u = Unit("watt")
        assert u.format() == "W"

    def test_format_ascii(self):
        u = Unit("watt")
        assert u.format(cf_units.UT_ASCII) == "W"

    def test_format_ut_names(self):
        u = Unit("watt")
        assert u.format(cf_units.UT_NAMES) == "watt"

    def test_format_unit_definition(self):
        u = Unit("watt")
        assert u.format(cf_units.UT_DEFINITION) == "m2.kg.s-3"

    def test_format_multiple_options(self):
        u = Unit("watt")
        assert (
            u.format([cf_units.UT_NAMES, cf_units.UT_DEFINITION])
            == "meter^2-kilogram-second^-3"
        )

    def test_format_multiple_options_utf8(self):
        u = Unit("watt")
        assert (
            u.format([cf_units.UT_NAMES, cf_units.UT_DEFINITION, cf_units.UT_UTF8])
            == "meter²·kilogram·second⁻³"
        )

    def test_format_unknown(self):
        u = Unit("?")
        assert u.format() == "unknown"

    def test_format_no_unit(self):
        u = Unit("nounit")
        assert u.format() == "no_unit"

    def test_format_names_utf8(self):
        u = Unit("m2")
        assert u.format([cf_units.UT_UTF8, cf_units.UT_NAMES]) == "meter²"

    def test_format_latin1(self):
        u = Unit("m2")
        assert u.format(cf_units.UT_LATIN1) == "m²"


class Test_name:
    def test_basic(self):
        u = Unit("newton")
        assert u.name == "newton"

    def test_unknown(self):
        u = Unit("unknown")
        assert u.name == "unknown"

    def test_no_unit(self):
        u = Unit("no unit")
        assert u.name == "no_unit"


class Test_symbol:
    def test_basic(self):
        u = Unit("joule")
        assert u.symbol == "J"

    def test_unknown(self):
        u = Unit("unknown")
        assert u.symbol == cf_units._UNKNOWN_UNIT_SYMBOL

    def test_no_unit(self):
        u = Unit("no unit")
        assert u.symbol == cf_units._NO_UNIT_SYMBOL


class Test_definition:
    def test_basic(self):
        u = Unit("joule")
        assert u.definition == "m2.kg.s-2"

    def test_unknown(self):
        u = Unit("unknown")
        assert u.definition == cf_units._UNKNOWN_UNIT_SYMBOL

    def test_no_unit(self):
        u = Unit("no unit")
        assert u.definition == cf_units._NO_UNIT_SYMBOL


class Test__apply_offset:
    def test_add_integer_offset(self):
        u = Unit("meter")
        assert u + 10 == "m @ 10"

    def test_add_float_offset(self):
        u = Unit("meter")
        assert u + 100.0 == "m @ 100"

    def test_not_numerical_offset(self):
        u = Unit("meter")
        with pytest.raises(TypeError, match="unsupported operand type"):
            operator.add(u, "not_a_number")

    def test_unit_unknown(self):
        u = Unit("unknown")
        assert u + 10 == "unknown"

    def test_no_unit(self):
        u = Unit("no unit")
        with pytest.raises(ValueError, match="Cannot offset"):
            operator.add(u, 10)


class Test_offset_by_time:
    def test_offset(self):
        u = Unit("hour")
        v = u.offset_by_time(cf_units.encode_time(2007, 1, 15, 12, 6, 0))
        assert v == "(3600 s) @ 20070115T120600.00000000 UTC"

    def test_not_numerical_offset(self):
        u = Unit("hour")
        with pytest.raises(TypeError, match="numeric type"):
            u.offset_by_time("not_a_number")

    def test_not_time_unit(self):
        u = Unit("mile")
        with pytest.raises(ValueError, match="Failed to offset"):
            u.offset_by_time(10)

    def test_unit_unknown(self):
        u = Unit("unknown")
        emsg = "Failed to offset"
        with pytest.raises(ValueError, match=emsg), suppress_errors():
            u.offset_by_time(cf_units.encode_time(1970, 1, 1, 0, 0, 0))

    def test_no_unit(self):
        u = Unit("no unit")
        emsg = "Failed to offset"
        with pytest.raises(ValueError, match=emsg), suppress_errors():
            u.offset_by_time(cf_units.encode_time(1970, 1, 1, 0, 0, 0))


class Test_invert:
    def test_basic(self):
        u = Unit("newton")
        assert u.invert() == "m-1.kg-1.s2"

    def test_double_invert(self):
        # Double-inverting a unit should take you back to where you started.
        u = Unit("newton")
        assert u.invert().invert() == u

    def test_invert_unknown(self):
        u = Unit("unknown")
        assert u.invert() == u

    def test_invert_no_unit(self):
        u = Unit("no unit")
        with pytest.raises(ValueError, match="Cannot invert"):
            u.invert()


class Test_root:
    def test_square_root(self):
        u = Unit("volt^2")
        assert u.root(2) == "V"

    def test_square_root_integer_float(self):
        u = Unit("volt^2")
        assert u.root(2.0) == "V"

    def test_not_numeric(self):
        u = Unit("volt")
        with pytest.raises(TypeError, match="numeric type"):
            u.offset_by_time("not_a_number")

    def test_not_integer(self):
        u = Unit("volt")
        with pytest.raises(TypeError, match="integer .* required"):
            u.root(1.2)

    def test_meaningless_operation(self):
        u = Unit("volt")
        emsg = "UT_MEANINGLESS"
        with pytest.raises(ValueError, match=emsg), suppress_errors():
            u.root(2)

    def test_unit_unknown(self):
        u = Unit("unknown")
        assert u.root(2) == u

    def test_no_unit(self):
        u = Unit("no unit")
        with pytest.raises(ValueError, match="Cannot take the root"):
            u.root(2)


class Test_log:
    def test_base_2(self):
        u = Unit("hPa")
        assert u.log(2) == "lb(re 100 Pa)"

    def test_base_10(self):
        u = Unit("hPa")
        assert u.log(10) == "lg(re 100 Pa)"

    def test_negative(self):
        u = Unit("hPa")
        msg = re.escape("Failed to calculate logarithmic base of Unit('hPa')")
        with pytest.raises(ValueError, match=msg):
            u.log(-1)

    def test_not_numeric(self):
        u = Unit("hPa")
        with pytest.raises(TypeError, match="numeric type"):
            u.log("not_a_number")

    def test_unit_unknown(self):
        u = Unit("unknown")
        assert u.log(10) == u

    def test_no_unit(self):
        u = Unit("no unit")
        emsg = "Cannot take the logarithm"
        with pytest.raises(ValueError, match=emsg):
            u.log(10)


class Test_multiply:
    def test_multiply_by_int(self):
        u = Unit("amp")
        assert (u * 10).format() == "10 A"

    def test_multiply_by_float(self):
        u = Unit("amp")
        assert (u * 100.0).format() == "100 A"

    def test_multiply_electrical_units(self):
        u = Unit("amp")
        v = Unit("volt")
        assert (u * v).format() == "W"

    def test_multiply_not_numeric(self):
        u = Unit("amp")
        with pytest.raises(ValueError, match="Failed to parse unit"):
            operator.mul(u, "not_a_number")

    def test_multiply_with_unknown_unit(self):
        u = Unit("unknown")
        v = Unit("meters")
        assert (u * v).is_unknown()
        assert (v * u).is_unknown()

    def test_multiply_with_no_unit(self):
        u = Unit("meters")
        v = Unit("no unit")
        with pytest.raises(ValueError, match="Cannot multiply"):
            operator.mul(u, v)
            operator.mul(v, u)

    def test_multiply_unknown_and_no_unit(self):
        u = Unit("unknown")
        v = Unit("no unit")
        with pytest.raises(ValueError, match="Cannot multiply"):
            operator.mul(u, v)
            operator.mul(v, u)


class Test_divide:
    def test_divide_by_int(self):
        u = Unit("watts")
        assert (u / 10).format() == "0.1 W"

    def test_divide_by_float(self):
        u = Unit("watts")
        assert (u / 100.0).format() == "0.01 W"

    def test_divide_electrical_units(self):
        u = Unit("watts")
        v = Unit("volts")
        assert (u / v).format() == "A"

    def test_divide_not_numeric(self):
        u = Unit("watts")
        with pytest.raises(ValueError, match="Failed to parse unit"):
            truediv(u, "not_a_number")

    def test_divide_with_unknown_unit(self):
        u = Unit("unknown")
        v = Unit("meters")
        assert (u / v).is_unknown()
        assert (v / u).is_unknown()

    def test_divide_with_no_unit(self):
        u = Unit("meters")
        v = Unit("no unit")
        with pytest.raises(ValueError, match="Cannot divide"):
            truediv(u, v)
            truediv(v, u)

    def test_divide_unknown_and_no_unit(self):
        u = Unit("unknown")
        v = Unit("no unit")
        with pytest.raises(ValueError, match="Cannot divide"):
            truediv(u, v)
            truediv(v, u)


class Test_power:
    def test_basic(self):
        u = Unit("m^2")
        assert u**0.5 == Unit("m")

    def test_integer_power(self):
        u = Unit("amp")
        assert u**2 == Unit("A^2")

    def test_float_power(self):
        u = Unit("amp")
        assert u**3.0 == Unit("A^3")

    def test_dimensionless(self):
        u = Unit("1")
        assert u**2 == u

    def test_power(self):
        u = Unit("amp")
        with pytest.raises(TypeError):
            operator.pow(u, Unit("m"))
        with pytest.raises(TypeError):
            operator.pow(u, Unit("unknown"))
        with pytest.raises(TypeError):
            operator.pow(u, Unit("no unit"))

    def test_not_numeric(self):
        u = Unit("m^2")
        emsg = "numeric value is required"
        with pytest.raises(TypeError, match=emsg):
            operator.pow(u, "not_a_number")

    def test_bad_power(self):
        u = Unit("m^2")
        emsg = "Cannot raise .* by a decimal"
        with pytest.raises(ValueError, match=emsg):
            operator.pow(u, 0.4)

    def test_unit_power(self):
        u = Unit("amp")
        v = Unit("m")
        emsg = "argument must be a string or a (real |)number"
        with pytest.raises(TypeError, match=emsg):
            operator.pow(u, v)


class Test_power__unknown:
    def setup_method(self):
        self.u = Unit("unknown")

    def test_integer_power(self):
        assert self.u**2 == Unit("unknown")

    def test_float_power(self):
        assert self.u**3.0 == Unit("unknown")

    def test_not_numeric(self):
        emsg = "numeric value is required"
        with pytest.raises(TypeError, match=emsg):
            operator.pow(self.u, "not_a_number")

    def test_bad_power(self):
        assert self.u**0.4 == self.u

    def test_unit_power(self):
        v = Unit("m")
        emsg = "argument must be a string or a (real |)number"
        with pytest.raises(TypeError, match=emsg):
            operator.pow(self.u, v)


class Test_power__no_unit:
    def setup_method(self):
        self.u = Unit("no unit")

    def test_integer_power(self):
        emsg = "Cannot raise .* a 'no-unit'"
        with pytest.raises(ValueError, match=emsg):
            operator.pow(self.u, 2)

    def test_float_power(self):
        emsg = "Cannot raise .* a 'no-unit'"
        with pytest.raises(ValueError, match=emsg):
            operator.pow(self.u, 3.0)

    def test_not_numeric(self):
        emsg = "numeric value is required"
        with pytest.raises(TypeError, match=emsg):
            operator.pow(self.u, "not_a_number")

    def test_bad_power(self):
        emsg = "Cannot raise .* a 'no-unit'"
        with pytest.raises(ValueError, match=emsg):
            operator.pow(self.u, 0.4)

    def test_unit_power(self):
        v = Unit("m")
        emsg = "argument must be a string or a (real |)number"
        with pytest.raises(TypeError, match=emsg):
            operator.pow(self.u, v)


class Test_copy:
    def test_basic(self):
        u = Unit("joule")
        assert copy.copy(u) == u

    def test_unit_unknown(self):
        u = Unit("unknown")
        assert copy.copy(u) == u
        assert copy.copy(u).is_unknown()

    def test_no_unit(self):
        u = Unit("no unit")
        assert copy.copy(u) == u
        assert copy.copy(u).is_no_unit()


class Test_stringify:
    def test___str__(self):
        u = Unit("meter")
        assert str(u) == "meter"

    def test___repr___basic(self):
        u = Unit("meter")
        assert repr(u) == "Unit('meter')"

    def test___repr___time_unit(self):
        u = Unit(
            "hours since 2007-01-15 12:06:00",
            calendar=cf_units.CALENDAR_GREGORIAN,
        )
        exp = "Unit('hours since 2007-01-15 12:06:00', calendar='standard')"
        assert repr(u) == exp


class Test_equality:
    def test_basic(self):
        u = Unit("meter")
        assert u == "meter"

    def test_equivalent_units(self):
        u = Unit("meter")
        v = Unit("m.s-1")
        w = Unit("hertz")
        assert u == v / w

    def test_non_equivalent_units(self):
        u = Unit("meter")
        v = Unit("amp")
        assert u != v

    def test_eq_cross_category(self):
        m = Unit("meter")
        u = Unit("unknown")
        n = Unit("no_unit")
        assert m != u
        assert m != n

    def test_unknown(self):
        u = Unit("unknown")
        assert u == "unknown"

    def test_no_unit(self):
        u = Unit("no_unit")
        assert u == "no_unit"

    def test_unknown_no_unit(self):
        u = Unit("unknown")
        v = Unit("no_unit")
        assert u != v

    def test_not_implemented(self):
        u = Unit("meter")
        assert u != {}


class Test_non_equality:
    def test_basic(self):
        u = Unit("meter")
        assert u == "meter"

    def test_non_equivalent_units(self):
        u = Unit("meter")
        v = Unit("amp")
        assert u != v

    def test_ne_cross_category(self):
        m = Unit("meter")
        u = Unit("unknown")
        n = Unit("no_unit")
        assert m != u
        assert m != n
        assert u != n

    def test_unknown(self):
        u = Unit("unknown")
        assert u == "unknown"

    def test_no_unit(self):
        u = Unit("no_unit")
        assert u == "no_unit"

    def test_not_implemented(self):
        u = Unit("meter")
        assert u != {}


class Test_convert:
    def test_convert_float(self):
        u = Unit("meter")
        v = Unit("mile")
        result = u.convert(1609.344, v)
        expected = 1.0
        assert result == expected

    def test_convert_int(self):
        u = Unit("mile")
        v = Unit("meter")
        result = u.convert(1, v)
        expected = 1609.344
        assert result == expected

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
        with pytest.raises(ValueError, match=emsg):
            u.convert(1.0, v)

    def test_unknown_units(self):
        u = Unit("unknown")
        v = Unit("no unit")
        m = Unit("m")
        val = 1.0
        emsg = "Unable to convert"
        with pytest.raises(ValueError, match=emsg):
            u.convert(val, m)
        with pytest.raises(ValueError, match=emsg):
            m.convert(val, u)
        with pytest.raises(ValueError, match=emsg):
            u.convert(val, v)

    def test_no_units(self):
        u = Unit("no unit")
        v = Unit("unknown")
        m = Unit("m")
        val = 1.0
        emsg = "Unable to convert"
        with pytest.raises(ValueError, match=emsg):
            u.convert(val, m)
        with pytest.raises(ValueError, match=emsg):
            m.convert(val, u)
        with pytest.raises(ValueError, match=emsg):
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
        with pytest.raises(ValueError, match=emsg):
            u.convert(u1point, v)


class Test_order:
    def test(self):
        m = Unit("meter")
        u = Unit("unknown")
        n = Unit("no_unit")
        start = [m, u, n]
        assert sorted(start) == [m, n, u]


class Test_is_unknown:
    def _check(self, unknown_str):
        u = Unit(unknown_str)
        assert u.is_unknown()

    def test_unknown_representations(self):
        representations = ["unknown", "?", "???"]
        for representation in representations:
            self._check(representation)

    def test_no_unit(self):
        u = Unit("no unit")
        assert not u.is_unknown()

    def test_known_unit(self):
        u = Unit("meters")
        assert not u.is_unknown()

    def test_no_ut_pointer(self):
        # Test that a unit that was poorly constructed has a
        # degree of tolerance by making it unknown.
        # https://github.com/SciTools/cf-units/issues/133 refers.
        assert Unit.__new__(Unit).is_unknown()


class Test_is_no_unit:
    def _check(self, no_unit_str):
        u = Unit(no_unit_str)
        assert u.is_no_unit()

    def test_no_unit_representations(self):
        representations = ["no_unit", "no unit", "no-unit", "nounit"]
        for representation in representations:
            self._check(representation)

    def test_unknown(self):
        u = Unit("unknown")
        assert not u.is_no_unit()

    def test_known_unit(self):
        u = Unit("meters")
        assert not u.is_no_unit()


class Test_is_udunits:
    def test_basic(self):
        u = Unit("meters")
        assert u.is_udunits()

    def test_unknown(self):
        u = Unit("unknown")
        assert not u.is_udunits()

    def test_no_unit(self):
        u = Unit("no_unit")
        assert not u.is_udunits()


class Test_is_time_reference:
    def test_basic(self):
        u = Unit("hours since epoch")
        assert u.is_time_reference()

    def test_not_time_reference(self):
        u = Unit("hours")
        assert not u.is_time_reference()

    def test_unknown(self):
        u = Unit("unknown")
        assert not u.is_time_reference()

    def test_no_unit(self):
        u = Unit("no_unit")
        assert not u.is_time_reference()


class Test_title:
    def test_basic(self):
        u = Unit("meter")
        assert u.title(10) == "10 meter"

    def test_time_unit(self):
        u = Unit("hours since epoch", calendar=cf_units.CALENDAR_STANDARD)
        assert u.title(10) == "1970-01-01 10:00:00"


class Test__immutable:
    def _set_attr(self, unit, name):
        setattr(unit, name, -999)
        raise ValueError(f"'Unit' attribute {name!r} is mutable!")

    def test_immutable(self):
        u = Unit("m")
        for name in dir(u):
            emsg = "Instances .* are immutable"
            with pytest.raises(AttributeError, match=emsg):
                self._set_attr(u, name)

    def test_common_hash(self):
        # Test different instances of length units (m) have a common hash.
        u1 = Unit("m")
        u2 = Unit("meter")
        u3 = copy.deepcopy(u1)
        h = set()
        for u in (u1, u2, u3):
            h.add(hash(u))
        assert len(h) == 1

        # Test different instances of electrical units (V) have a common hash.
        v1 = Unit("V")
        v2 = Unit("volt")
        for u in (v1, v2):
            h.add(hash(u))
        assert len(h) == 2


class Test__inplace:
    # Test shared memory for conversion operations.

    def test(self):
        # Check conversions do not change original object.
        c = Unit("deg_c")
        f = Unit("deg_f")

        orig = np.arange(3, dtype=np.float32)

        # Test arrays are not equal without inplace conversions.
        converted = c.convert(orig, f)

        emsg = "Arrays are not equal"
        with pytest.raises(AssertionError, match=emsg):
            np.testing.assert_array_equal(orig, converted)
        assert not np.may_share_memory(orig, converted)

        # Test inplace conversion alters the original array.
        converted = c.convert(orig, f, inplace=True)
        np.testing.assert_array_equal(orig, converted)
        assert np.may_share_memory(orig, converted)

    def test_multidim_masked(self):
        c = Unit("deg_c")
        f = Unit("deg_f")

        # Manufacture a Fortran-ordered nd-array to be converted.
        orig = (
            np.ma.masked_array(np.arange(4, dtype=np.float32), mask=[1, 0, 0, 1])
            .reshape([2, 2])
            .T
        )

        # Test arrays are not equal without inplace conversions.
        converted = c.convert(orig, f)

        emsg = "Arrays are not equal"
        with pytest.raises(AssertionError, match=emsg):
            np.testing.assert_array_equal(orig.data, converted.data)
        assert not np.may_share_memory(orig, converted)

        # Test inplace conversion alters the original array.
        converted = c.convert(orig, f, inplace=True)
        np.testing.assert_array_equal(orig.data, converted.data)
        assert np.may_share_memory(orig, converted)

    def test_foreign_endian(self):
        c = Unit("deg_c")
        f = Unit("deg_f")

        # Manufacture a non-native byte-order array to be converted.
        arr = np.arange(4, dtype=np.float32)
        orig = arr.view(arr.dtype.newbyteorder("S"))

        emsg = (
            "Unable to convert non-native byte ordered array in-place. "
            "Consider byte-swapping first."
        )
        with pytest.raises(ValueError, match=emsg):
            c.convert(orig, f, inplace=True)

        # Test we can do this when not-inplace
        c.convert(orig, f)


class TestTimeEncoding:
    def test_encode_time(self):
        result = cf_units.encode_time(2006, 1, 15, 12, 6, 0)
        assert result == 159019560.0

    def test_encode_date(self):
        result = cf_units.encode_date(2006, 1, 15)
        assert result == 158976000.0

    def test_encode_clock(self):
        result = cf_units.encode_clock(12, 6, 0)
        assert result == 43560.0

    def test_decode_time(self):
        result = cf_units.decode_time(158976000.0 + 43560.0)
        year, month, day, hour, min, sec, res = result
        assert (year, month, day, hour, min, sec) == (2006, 1, 15, 12, 6, 0)


class TestNumsAndDates:
    def test_num2date(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00",
            calendar=cf_units.CALENDAR_GREGORIAN,
        )
        res = u.num2date(1)
        assert str(res) == "2010-11-02 13:00:00"
        assert res.calendar == "standard"
        assert isinstance(res, cftime.datetime)

    def test_num2date_py_datetime_type(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00",
            calendar=cf_units.CALENDAR_STANDARD,
        )
        res = u.num2date(1, only_use_cftime_datetimes=False)
        assert str(res) == "2010-11-02 13:00:00"
        assert isinstance(res, datetime.datetime)

    def test_num2date_wrong_calendar(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00",
            calendar=cf_units.CALENDAR_360_DAY,
        )
        with pytest.raises(ValueError, match="illegal calendar or reference date"):
            u.num2date(
                1,
                only_use_cftime_datetimes=False,
                only_use_python_datetimes=True,
            )

    def test_date2num(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00",
            calendar=cf_units.CALENDAR_STANDARD,
        )
        d = datetime.datetime(2010, 11, 2, 13, 0, 0)
        assert str(u.num2date(u.date2num(d))) == "2010-11-02 13:00:00"

    def test_num2pydate_simple(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00",
            calendar=cf_units.CALENDAR_STANDARD,
        )
        result = u.num2pydate(1)
        expected = datetime.datetime(2010, 11, 2, 13)
        assert result == expected
        assert isinstance(result, datetime.datetime)

    def test_num2pydate_wrong_calendar(self):
        u = Unit(
            "hours since 2010-11-02 12:00:00",
            calendar=cf_units.CALENDAR_360_DAY,
        )
        with pytest.raises(ValueError, match="illegal calendar or reference date"):
            u.num2pydate(1)


class Test_as_unit:
    def test_already_unit(self):
        u = Unit("m")
        result = cf_units.as_unit(u)
        assert result is u

    def test_known_unit_str(self):
        u_str = "m"
        expected = Unit("m")
        result = cf_units.as_unit(u_str)
        assert expected == result

    def test_not_unit_str(self):
        u_str = "wibble"
        emsg = "Failed to parse unit"
        with pytest.raises(ValueError, match=emsg):
            cf_units.as_unit(u_str)

    def test_unknown_str(self):
        u_str = "unknown"
        expected = Unit("unknown")
        result = cf_units.as_unit(u_str)
        assert expected == result

    def test_no_unit_str(self):
        u_str = "no_unit"
        expected = Unit("no_unit")
        result = cf_units.as_unit(u_str)
        assert expected == result


class Test_is_time:
    def test_basic(self):
        u = Unit("hours")
        assert u.is_time()

    def test_not_time_unit(self):
        u = Unit("meters")
        assert not u.is_time()

    def test_unknown(self):
        u = Unit("unknown")
        assert not u.is_time()

    def test_no_unit(self):
        u = Unit("no_unit")
        assert not u.is_time()


class Test_is_vertical:
    def test_pressure_unit(self):
        u = Unit("millibar")
        assert u.is_vertical()

    def test_length_unit(self):
        u = Unit("meters")
        assert u.is_vertical()

    def test_not_vertical_unit(self):
        u = Unit("hours")
        assert not u.is_vertical()

    def test_unknown(self):
        u = Unit("unknown")
        assert not u.is_vertical()

    def test_no_unit(self):
        u = Unit("no_unit")
        assert not u.is_vertical()
