# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Unit tests for the `cf_units._udunits2` module.

In most cases, we don't test the correctness
of the operations, only that they return valid objects or raise an
exception where expected."""

import errno

import numpy as np
import pytest

from cf_units import _udunits2 as _ud
from cf_units.config import get_xml_path

_ud.set_error_message_handler(_ud.ignore)


class Test_get_system:
    """
    Test case for operations which create a system object.

    """

    def test_read_xml(self):
        try:
            system = _ud.read_xml()
        except _ud.UdunitsError:
            system = _ud.read_xml(get_xml_path())

        assert system is not None

    def test_read_xml_invalid_path(self):
        with pytest.raises(_ud.UdunitsError, match="UT_OPEN_ARG") as ex:
            _ud.read_xml(b"/not/a/path.xml")

        assert ex.value.errnum == errno.ENOENT


class Test_system:
    """
    Test case for system operations.

    """

    def setup_method(self):
        try:
            self.system = _ud.read_xml()
        except _ud.UdunitsError:
            self.system = _ud.read_xml(get_xml_path())

    def test_get_unit_by_name(self):
        unit = _ud.get_unit_by_name(self.system, b"metre")

        assert unit is not None

    def test_get_unit_by_name_invalid_unit(self):
        with pytest.raises(_ud.UdunitsError):
            _ud.get_unit_by_name(self.system, b"jigawatt")

    def test_parse(self):
        unit = _ud.parse(self.system, b"gigawatt", _ud.UT_ASCII)

        assert unit is not None

    def test_parse_latin1(self):
        angstrom = _ud.parse(self.system, b"\xe5ngstr\xF6m", _ud.UT_LATIN1)

        assert angstrom is not None

    def test_parse_ISO_8859_1(self):
        angstrom = _ud.parse(self.system, b"\xe5ngstr\xF6m", _ud.UT_ISO_8859_1)

        assert angstrom is not None

    def test_parse_UTF8(self):
        angstrom = _ud.parse(
            self.system, b"\xc3\xa5ngstr\xc3\xb6m", _ud.UT_UTF8
        )

        assert angstrom is not None

    def test_parse_invalid_unit(self):
        with pytest.raises(_ud.UdunitsError):
            _ud.parse(self.system, b"jigawatt", _ud.UT_ASCII)


class Test_unit:
    """
    Test case for unit operations.

    """

    def setup_method(self):
        try:
            self.system = _ud.read_xml()
        except _ud.UdunitsError:
            self.system = _ud.read_xml(get_xml_path())

        self.metre = _ud.get_unit_by_name(self.system, b"metre")
        self.yard = _ud.get_unit_by_name(self.system, b"yard")
        self.second = _ud.get_unit_by_name(self.system, b"second")

    def test_clone(self):
        metre_clone = _ud.clone(self.metre)

        assert metre_clone is not self.metre

    def test_is_dimensionless_true(self):
        radian = _ud.get_unit_by_name(self.system, b"radian")
        assert _ud.is_dimensionless(radian)

    def test_is_dimensionless_false(self):
        assert not _ud.is_dimensionless(self.metre)

    def test_compare_same_unit(self):
        assert _ud.compare(self.metre, self.metre) == 0

    def test_compare_diff_unit(self):
        comp = _ud.compare(self.metre, self.second)
        comp_r = _ud.compare(self.second, self.metre)

        assert comp != 0
        assert comp_r != 0
        # m < s iff s > m
        assert (comp < 0) == (comp_r > 0)

    def test_are_convertible_true(self):
        assert _ud.are_convertible(self.metre, self.yard)

    def test_are_convertible_false(self):
        assert not _ud.are_convertible(self.metre, self.second)

    def test_get_converter_valid(self):
        _ud.get_converter(self.metre, self.yard)

    def test_get_converter_invalid(self):
        with pytest.raises(_ud.UdunitsError, match="UT_MEANINGLESS"):
            _ud.get_converter(self.metre, self.second)

    def test_scale(self):
        mm = _ud.scale(0.001, self.metre)

        assert mm is not None

    def test_offset(self):
        kelvin = _ud.get_unit_by_name(self.system, b"kelvin")
        celsius = _ud.offset(kelvin, 273.15)

        assert celsius is not None

    def test_offset_by_time_valid(self):
        time_since = _ud.offset_by_time(self.second, -31622400.0)

        assert time_since is not None

    @pytest.mark.xfail
    def test_offset_by_time_invalid(self):
        with pytest.raises(_ud.UdunitsError, match="UT_MEANINGLESS"):
            _ud.offset_by_time(self.metre, -31622400.0)

        # The udunits package should set a status of UT_MEANINGLESS, according
        # to the documentation. However, it is setting it to UT_SUCCESS.

    def test_multiply(self):
        metre_second = _ud.multiply(self.metre, self.second)

        assert metre_second is not None

    def test_invert(self):
        hertz = _ud.invert(self.second)

        assert hertz is not None

    def test_divide(self):
        metres_per_second = _ud.divide(self.metre, self.second)

        assert metres_per_second is not None

    def test_raise_(self):
        sq_metre = _ud.raise_(self.metre, 2)

        assert sq_metre is not None

    def test_root(self):
        hectare = _ud.get_unit_by_name(self.system, b"hectare")
        hundred_metre = _ud.root(hectare, 2)

        assert hundred_metre is not None

    def test_log(self):
        log_metre = _ud.log(2.7182818, self.metre)

        assert log_metre is not None

    def test_format(self):
        pascal = _ud.get_unit_by_name(self.system, b"pascal")
        symb = _ud.format(pascal)
        name = _ud.format(pascal, _ud.UT_NAMES)
        defn = _ud.format(pascal, _ud.UT_DEFINITION)
        name_defn = _ud.format(pascal, _ud.UT_DEFINITION | _ud.UT_NAMES)

        assert symb == b"Pa"
        assert name == b"pascal"
        assert defn == b"m-1.kg.s-2"
        assert name_defn == b"meter^-1-kilogram-second^-2"


class Test_time_encoding:
    def setup_method(self):
        self.year, self.month, self.day = 2000, 1, 1
        self.date_encoding = -31622400.0
        self.hours, self.minutes, self.seconds = 12, 34, 56
        self.clock_encoding = 45296.0

    def test_encode_date(self):
        res_date_encoding = _ud.encode_date(self.year, self.month, self.day)

        assert self.date_encoding == res_date_encoding

    def test_encode_clock(self):
        res_clock_encoding = _ud.encode_clock(
            self.hours, self.minutes, self.seconds
        )

        assert self.clock_encoding == res_clock_encoding

    def test_encode_time(self):
        res_time_encoding = _ud.encode_time(
            self.year,
            self.month,
            self.day,
            self.hours,
            self.minutes,
            self.seconds,
        )

        assert self.clock_encoding + self.date_encoding == res_time_encoding

    def test_decode_time(self):
        (
            res_year,
            res_month,
            res_day,
            res_hours,
            res_minutes,
            res_seconds,
            res_resolution,
        ) = _ud.decode_time(self.date_encoding + self.clock_encoding)

        assert (res_year, res_month, res_day, res_hours, res_minutes) == (
            self.year,
            self.month,
            self.day,
            self.hours,
            self.minutes,
        )
        assert (
            res_seconds - res_resolution
            < self.seconds
            < res_seconds + res_resolution
        )


class Test_convert:
    """
    Test case for convert operations.

    """

    def setup_method(self):
        try:
            system = _ud.read_xml()
        except _ud.UdunitsError:
            system = _ud.read_xml(get_xml_path())

        metre = _ud.get_unit_by_name(system, b"metre")
        yard = _ud.get_unit_by_name(system, b"yard")
        self.converter = _ud.get_converter(metre, yard)
        self.factor = 1.0936132669448853

    def test_convert_float(self):
        res = _ud.convert_float(self.converter, 2.5)
        np.testing.assert_approx_equal(2.5 * self.factor, res)

    def test_convert_floats(self):
        arr = np.array([2.5, 5.0, 10.0], dtype=np.float32)
        res = np.empty_like(arr)
        _ud.convert_floats(self.converter, arr, res)
        np.testing.assert_array_almost_equal(arr * self.factor, res)

    def test_convert_double(self):
        res = _ud.convert_double(self.converter, 2.5)
        np.testing.assert_approx_equal(2.5 * self.factor, res)

    def test_convert_doubles(self):
        arr = np.array([2.5, 5.0, 10.0], dtype=np.float64)
        res = np.empty_like(arr)
        _ud.convert_doubles(self.converter, arr, res)
        np.testing.assert_array_almost_equal(arr * self.factor, res)
