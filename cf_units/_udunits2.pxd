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

cdef extern from "udunits2.h":
    ctypedef struct ut_system:
        pass

    ctypedef union ut_unit:
        pass

    ctypedef union cv_converter:
        pass

    ctypedef enum ut_status:
        pass

    ctypedef enum ut_encoding:
        pass

    ctypedef void *ut_error_message_handler

    ut_system* ut_read_xml(char* path)

    void ut_free_system(ut_system* system)

    ut_unit* ut_get_unit_by_name(ut_system* system, char* name)

    ut_unit* ut_clone(ut_unit* unit)

    void ut_free(ut_unit* unit)

    int ut_is_dimensionless(ut_unit* unit)

    int ut_compare(ut_unit* unit1, ut_unit* unit2)

    int ut_are_convertible(ut_unit* unit1, ut_unit* unit2)

    cv_converter* ut_get_converter(ut_unit* fr, ut_unit* to)

    ut_unit* ut_scale(double factor, ut_unit* unit)

    ut_unit* ut_offset(ut_unit* unit, double offset)

    ut_unit* ut_offset_by_time(ut_unit* unit, double origin)

    ut_unit* ut_multiply(ut_unit* unit1, ut_unit* unit2)

    ut_unit* ut_invert(ut_unit* unit)

    ut_unit* ut_divide(ut_unit* numer, ut_unit* denom)

    ut_unit* ut_raise(ut_unit* unit, int power)

    ut_unit* ut_root(ut_unit* unit, int root)

    ut_unit* ut_log(double base, ut_unit* reference)

    ut_unit* ut_parse(ut_system* system, const char* string,
                      ut_encoding encoding)

    int ut_format(ut_unit* unit, char* buf, size_t size, unsigned opts)

    double ut_encode_date(int year, int month, int day)

    double ut_encode_clock(int hours, int minutes, double seconds)

    double ut_encode_time(int year, int month, int day,
                          int hour, int minute, double second)

    void ut_decode_time(double value,
                        int* year, int* month, int* day,
                        int* hour, int* minute, double* second,
                        double* resolution)

    ut_status ut_get_status()

    ut_error_message_handler ut_ignore

    ut_error_message_handler ut_set_error_message_handler(ut_error_message_handler handler)

    float cv_convert_float(cv_converter* converter, float value)

    double cv_convert_double(cv_converter* converter, double value)

    float* cv_convert_floats(cv_converter* converter, float* in_, size_t count, float* out)

    double* cv_convert_doubles(cv_converter* converter, double* const in_, size_t count, double* out)

    void cv_free(cv_converter* conv)

