# (C) British Crown Copyright 2017 - 2018, Met Office
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
"""Unit tests for the `cf_units._udunits2` module.

In most cases, we don't test the correctness
of the operations, only that they return valid objects or raise an
exception where expected."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import os
import unittest

import numpy as np

from cf_units import _udunits2 as _ud


_ud.set_error_message_handler(_ud.ignore)


class Test_get_system(unittest.TestCase):
    """
    Test case for operations which create a system object.

    """
    def test_read_xml(self):
        system = _ud.read_xml()

        self.assertIsNotNone(system)

    def test_read_xml_invalid_path(self):
        with self.assertRaises(_ud.UdunitsError) as cm:
            _ud.read_xml(b'/not/a/path.xml')
        ex = cm.exception

        self.assertEqual(ex.status_msg(), 'UT_OPEN_ARG')
        self.assertEqual(ex.errnum, os.errno.ENOENT)


class Test_system(unittest.TestCase):
    """
    Test case for system operations.

    """
    def setUp(self):
        self.system = _ud.read_xml()

    def test_get_unit_by_name(self):
        unit = _ud.get_unit_by_name(self.system, b'metre')

        self.assertIsNotNone(unit)

    def test_get_unit_by_name_invalid_unit(self):
        with self.assertRaises(_ud.UdunitsError):
            _ud.get_unit_by_name(self.system, b'jigawatt')

    def test_parse(self):
        unit = _ud.parse(self.system, b'gigawatt', _ud.UT_ASCII)

        self.assertIsNotNone(unit)

    def test_parse_latin1(self):
        angstrom = _ud.parse(self.system, b'\xe5ngstr\xF6m', _ud.UT_LATIN1)

        self.assertIsNotNone(angstrom)

    def test_parse_ISO_8859_1(self):
        angstrom = _ud.parse(self.system, b'\xe5ngstr\xF6m', _ud.UT_ISO_8859_1)

        self.assertIsNotNone(angstrom)

    def test_parse_UTF8(self):
        angstrom = _ud.parse(self.system, b'\xc3\xa5ngstr\xc3\xb6m',
                             _ud.UT_UTF8)

        self.assertIsNotNone(angstrom)

    def test_parse_invalid_unit(self):
        with self.assertRaises(_ud.UdunitsError):
            unit = _ud.parse(self.system, b'jigawatt',
                             _ud.UT_ASCII)


class Test_unit(unittest.TestCase):
    """
    Test case for unit operations.

    """
    def setUp(self):
        self.system = _ud.read_xml()
        self.metre = _ud.get_unit_by_name(self.system, b'metre')
        self.yard = _ud.get_unit_by_name(self.system, b'yard')
        self.second = _ud.get_unit_by_name(self.system, b'second')

    def test_clone(self):
        metre_clone = _ud.clone(self.metre)

        self.assertIsNot(metre_clone, self.metre)

    def test_is_dimensionless_true(self):
        radian = _ud.get_unit_by_name(self.system, b'radian')
        self.assertTrue(_ud.is_dimensionless(radian))

    def test_is_dimensionless_false(self):
        self.assertFalse(_ud.is_dimensionless(self.metre))

    def test_compare_same_unit(self):
        self.assertEqual(_ud.compare(self.metre, self.metre), 0)

    def test_compare_diff_unit(self):
        comp = _ud.compare(self.metre, self.second)
        comp_r = _ud.compare(self.second, self.metre)

        self.assertNotEqual(comp, 0)
        self.assertNotEqual(comp_r, 0)
        # m < s iff s > m
        self.assertEqual(comp < 0, comp_r > 0)

    def test_are_convertible_true(self):
        self.assertTrue(_ud.are_convertible(self.metre, self.yard))

    def test_are_convertible_false(self):
        self.assertFalse(_ud.are_convertible(self.metre, self.second))

    def test_get_converter_valid(self):
        cv = _ud.get_converter(self.metre, self.yard)

    def test_get_converter_invalid(self):
        with self.assertRaises(_ud.UdunitsError) as cm:
            _ud.get_converter(self.metre, self.second)
        ex = cm.exception

        self.assertEqual(ex.status_msg(), 'UT_MEANINGLESS')

    def test_scale(self):
        mm = _ud.scale(0.001, self.metre)

        self.assertIsNotNone(mm)

    def test_offset(self):
        kelvin = _ud.get_unit_by_name(self.system, b'kelvin')
        celsius = _ud.offset(kelvin, 273.15)

        self.assertIsNotNone(celsius)

    def test_offset_by_time_valid(self):
        time_since = _ud.offset_by_time(self.second, -31622400.0)

        self.assertIsNotNone(time_since)

    def test_offset_by_time_invalid(self):
        with self.assertRaises(_ud.UdunitsError) as cm:
            _ud.offset_by_time(self.metre, -31622400.0)
        ex = cm.exception

        # The udunits package should set a status of UT_MEANINGLESS, according
        # to the documentation. However, it is setting it to UT_SUCCESS.
        # self.assertEqual(ex.status_msg(), 'UT_MEANINGLESS')

    def test_multiply(self):
        metre_second = _ud.multiply(self.metre, self.second)

        self.assertIsNotNone(metre_second)

    def test_invert(self):
        hertz = _ud.invert(self.second)

        self.assertIsNotNone(hertz)

    def test_divide(self):
        metres_per_second = _ud.divide(self.metre, self.second)

        self.assertIsNotNone(metres_per_second)

    def test_raise_(self):
        sq_metre = _ud.raise_(self.metre, 2)

        self.assertIsNotNone(sq_metre)

    def test_root(self):
        hectare = _ud.get_unit_by_name(self.system, b'hectare')
        hundred_metre = _ud.root(hectare, 2)

        self.assertIsNotNone(hundred_metre)

    def test_log(self):
        log_metre = _ud.log(2.7182818, self.metre)

        self.assertIsNotNone(log_metre)

    def test_format(self):
        pascal = _ud.get_unit_by_name(self.system, b'pascal')
        symb = _ud.format(pascal)
        name = _ud.format(pascal, _ud.UT_NAMES)
        defn = _ud.format(pascal, _ud.UT_DEFINITION)
        name_defn = _ud.format(pascal, _ud.UT_DEFINITION | _ud.UT_NAMES)

        self.assertEqual(symb, b'Pa')
        self.assertEqual(name, b'pascal')
        self.assertEqual(defn, b'm-1.kg.s-2')
        self.assertEqual(name_defn, b'meter^-1-kilogram-second^-2')


class Test_time_encoding(unittest.TestCase):

    def setUp(self):
        self.year, self.month, self.day = 2000, 1, 1
        self.date_encoding = -31622400.0
        self.hours, self.minutes, self.seconds = 12, 34, 56
        self.clock_encoding = 45296.0

    def test_encode_date(self):
        res_date_encoding = _ud.encode_date(self.year, self.month, self.day)

        self.assertEqual(self.date_encoding, res_date_encoding)

    def test_encode_clock(self):
        res_clock_encoding = _ud.encode_clock(self.hours, self.minutes,
                                              self.seconds)

        self.assertEqual(self.clock_encoding, res_clock_encoding)

    def test_encode_time(self):
        res_time_encoding = _ud.encode_time(self.year, self.month, self.day,
                                            self.hours, self.minutes,
                                            self.seconds)

        self.assertEqual(self.clock_encoding + self.date_encoding,
                         res_time_encoding)

    def test_decode_time(self):
        res_year, res_month, res_day, res_hours, res_minutes, res_seconds,\
            res_resolution =\
            _ud.decode_time(self.date_encoding + self.clock_encoding)

        self.assertEqual(
            (res_year, res_month, res_day, res_hours, res_minutes),
            (self.year, self.month, self.day, self.hours, self.minutes))
        self.assertTrue(res_seconds - res_resolution < self.seconds <
                        res_seconds + res_resolution)


class Test_convert(unittest.TestCase):
    """
    Test case for convert operations.

    """
    def setUp(self):
        system = _ud.read_xml()
        metre = _ud.get_unit_by_name(system, b'metre')
        yard = _ud.get_unit_by_name(system, b'yard')
        self.converter = _ud.get_converter(metre, yard)
        self.factor = 1.0936132669448853

    def test_convert_float(self):
        res = _ud.convert_float(self.converter, 2.5)
        np.testing.assert_approx_equal(2.5 * self.factor, res)

    def test_convert_floats(self):
        arr = np.array([2.5, 5., 10.], dtype=np.float32)
        res = np.empty_like(arr)
        _ud.convert_floats(self.converter, arr, res)
        np.testing.assert_array_almost_equal(arr * self.factor, res)

    def test_convert_double(self):
        res = _ud.convert_double(self.converter, 2.5)
        np.testing.assert_approx_equal(2.5 * self.factor, res)

    def test_convert_doubles(self):
        arr = np.array([2.5, 5., 10.], dtype=np.float64)
        res = np.empty_like(arr)
        _ud.convert_doubles(self.converter, arr, res)
        np.testing.assert_array_almost_equal(arr * self.factor, res)


if __name__ == '__main__':
    unittest.main()
