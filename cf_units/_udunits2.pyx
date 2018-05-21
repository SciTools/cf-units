# (C) British Crown Copyright 2016-2017, Met Office
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
"""
Units of measure.

Wrapper for Unidata/UCAR UDUNITS-2.

See also: `UDUNITS-2
<http://www.unidata.ucar.edu/software/udunits/udunits-2/udunits2.html>`_.

"""

# cython: nonecheck=True

import numpy as np
cimport numpy as np

from libc cimport errno, string


cdef int _STRING_BUFFER_DEPTH = 128
cdef list _UT_STATUS = ['UT_SUCCESS', 'UT_BAD_ARG', 'UT_EXISTS', 'UT_NO_UNIT',
                        'UT_OS', 'UT_NOT_SAME_SYSTEM', 'UT_MEANINGLESS',
                        'UT_NO_SECOND', 'UT_VISIT_ERROR', 'UT_CANT_FORMAT',
                        'UT_SYNTAX', 'UT_UNKNOWN', 'UT_OPEN_ARG',
                        'UT_OPEN_ENV', 'UT_OPEN_DEFAULT', 'UT_PARSE']

UT_ASCII = 0
UT_ISO_8859_1 = 1
UT_LATIN1 = UT_ISO_8859_1
UT_UTF8 = 2

UT_NAMES = 4
UT_DEFINITION = 8


##### Wrapper classes #####

cdef class System:
    """
    Wrapper class for UDUNITS-2 ut_system. Calls ut_free_system() on
    deallocation.

    """
    cdef ut_system *csystem

    def __cinit__(self):
        self.csystem = NULL

    def __dealloc__(self):
        ut_free_system(self.csystem)


cdef class Unit:
    """
    Wrapper class for UDUNITS-2 ut_unit. Calls ut_free() on
    deallocation.

    """
    cdef ut_unit *cunit
    cdef System system

    def __cinit__(self):
        self.cunit = NULL
        self.system = None

    def __dealloc__(self):
        ut_free(self.cunit)


cdef class Converter:
    """
    Wrapper class for UDUNITS-2 cv_converter. Calls cv_free() on
    deallocation.

    """
    cdef cv_converter *cconverter

    def __cinit__(self):
        self.cconverter = NULL

    def __dealloc__(self):
        cv_free(self.cconverter)


cdef class ErrorMessageHandler:
    """
    Wrapper class for UDUNITS-2 ut_error_message_handler typedef.

    """
    cdef ut_error_message_handler chandler

    def __cinit__(self):
        self.chandler = NULL

# The following wrap_* functions should be called directly after the api call
# which returned their arguments, in order that in the event of an error the
# correct ut_status and errno values are retreived by _raise_error()

cdef System wrap_system(ut_system* csystem):
    if csystem is NULL:
        _raise_error()
    cdef System sytem = System()
    sytem.csystem = csystem
    return sytem

cdef Unit wrap_unit(System system, ut_unit* cunit):
    if cunit is NULL:
        _raise_error()
    cdef Unit unit = Unit()
    unit.cunit = cunit
    unit.system = system
    return unit

cdef Converter wrap_converter(cv_converter* cconverter):
    if cconverter is NULL:
        _raise_error()
    cdef Converter converter = Converter()
    converter.cconverter = cconverter
    return converter

cdef ErrorMessageHandler _ignore = ErrorMessageHandler()
_ignore.chandler = ut_ignore
ignore = _ignore

# Convenience object to avoid having to do None handling either here or in
# user code
NULL_UNIT = Unit()


##### Exception class #####

class UdunitsError(Exception):
    """
    UDUNITS-2 call resulted in an error.

    Attributes:

    * status:
        The UDUNITS-2 ut_status value which resulted from the error.
    * errnum:
        The errno value which resulted from the error.

    """
    def __init__(self, ut_status status, int errnum):
        self.status = status
        self.errnum = errnum

    def status_msg(self):
        """
        String representation of the UDUNITS-2 ut_status value which resulted
        from the error.

        """
        if 0 <= self.status < len(_UT_STATUS):
            return _UT_STATUS[self.status]
        else:
            return 'UNKNOWN'

    def error_msg(self):
        """
        The message string associated with the errno value which resulted from
        the error.

        """
        return string.strerror(self.errnum) if self.errnum else ''

    def __str__(self):
        str_err = ': {}'.format(string.strerror(self.errnum)) \
                  if self.errnum else ''
        return '{}{}'.format(self.status_msg(), str_err)
        

def _raise_error():
    """
    Raise a UdunitsError with the current value of errno and ut_status

    """
    errnum = errno.errno
    errno.errno = 0
    status = ut_get_status()
    raise UdunitsError(status, errnum)


##### Wrapper functions #####

# The following functions wrap the corresponding ut_* or cv_* api calls.
# See the UDUNITS-2 documentation for details.

def read_xml(char* path=NULL):
    cdef ut_system* csystem = ut_read_xml(path)
    return wrap_system(csystem)

def get_unit_by_name(System system, char* name):
    cdef ut_unit* cunit = ut_get_unit_by_name(system.csystem, name)
    return wrap_unit(system, cunit)

def clone(Unit unit):
    cdef ut_unit* cunit = ut_clone(unit.cunit)
    return wrap_unit(unit.system, cunit)

def is_dimensionless(Unit unit):
    return <bint>ut_is_dimensionless(unit.cunit)

def compare(Unit unit1, Unit unit2):
    return ut_compare(unit1.cunit, unit2.cunit)

def are_convertible(Unit unit1, Unit unit2):
    return <bint>ut_are_convertible(unit1.cunit, unit2.cunit)

def get_converter(Unit fr, Unit to):
    cdef cv_converter* cconverter = ut_get_converter(fr.cunit, to.cunit)
    return wrap_converter(cconverter)

def scale(double factor, Unit unit):
    cdef ut_unit* cunit = ut_scale(factor, unit.cunit)
    return wrap_unit(unit.system, cunit)

def offset(Unit unit, double offset):
    cdef ut_unit* cunit = ut_offset(unit.cunit, offset)
    return wrap_unit(unit.system, cunit)

def offset_by_time(Unit unit, double origin):
    cdef ut_unit* cunit = ut_offset_by_time(unit.cunit, origin)
    return wrap_unit(unit.system, cunit)

def multiply(Unit unit1, Unit unit2):
    cdef ut_unit* cunit = ut_multiply(unit1.cunit, unit2.cunit)
    return wrap_unit(unit1.system, cunit)

def invert(Unit unit):
    cdef ut_unit* cunit =  ut_invert(unit.cunit)
    return wrap_unit(unit.system, cunit)

def divide(Unit numer, Unit denom):
    cdef ut_unit* cunit = ut_divide(numer.cunit, denom.cunit)
    return wrap_unit(numer.system, cunit)

def raise_(Unit unit, int power):
    cdef ut_unit* cunit = ut_raise(unit.cunit, power)
    return wrap_unit(unit.system, cunit)

def root(Unit unit, int root):
    cdef ut_unit* cunit = ut_root(unit.cunit, root)
    return wrap_unit(unit.system, cunit)

def log(double base, Unit reference):
    cdef ut_unit* cunit = ut_log(base, reference.cunit)
    return wrap_unit(reference.system, cunit)


def parse(System system, char* string, ut_encoding encoding):
    cdef ut_unit* cunit = ut_parse(system.csystem, string, encoding)
    return wrap_unit(system, cunit)

def format(Unit unit, unsigned opts=0):
    cdef bytearray buf = bytearray(_STRING_BUFFER_DEPTH)
    n = ut_format(unit.cunit, buf, len(buf), opts)
    if n >= _STRING_BUFFER_DEPTH:
        buf = bytearray(n + 1)
        n = ut_format(unit.cunit, buf, len(buf), opts)
    if n == -1:
        _raise_error()
    return bytes(buf[:n])

def encode_date(int year, int month, int day):
    return ut_encode_date(year, month, day)

def encode_clock(int hours, int minutes, double seconds):
    return ut_encode_clock(hours, minutes, seconds)

def encode_time(int year, int month, int day,
                int hour, int minute, double second):
    return ut_encode_time(year, month, day, hour, minute, second)

def decode_time(double value):
    cdef int year, month, day, hour, minute
    cdef double second, resolution
    ut_decode_time(value, &year, &month, &day, &hour, &minute, &second,
                   &resolution)
    return (year, month, day, hour, minute, second, resolution)

def set_error_message_handler(ErrorMessageHandler handler):
    cdef ErrorMessageHandler result = ErrorMessageHandler()
    result.chandler = ut_set_error_message_handler(handler.chandler)
    return result

def convert_float(Converter converter, float value):
    return cv_convert_float(converter.cconverter, value)

def convert_floats(Converter converter, np.ndarray[np.float32_t] in_, np.ndarray[np.float32_t] out):
    cv_convert_floats(converter.cconverter, <float*> in_.data, in_.size, <float*> out.data)
    return out

def convert_double(Converter converter, double value):
    return cv_convert_double(converter.cconverter, value)

def convert_doubles(Converter converter, np.ndarray[np.float64_t] in_, np.ndarray[np.float64_t] out):
    cv_convert_doubles(converter.cconverter, <double*> in_.data, in_.size, <double*> out.data)
    return out
