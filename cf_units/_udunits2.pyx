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


##### Wrapper classes #####

cdef class System:
    cdef ut_system *csystem

    def __cinit__(self):
        self.csystem = NULL

    def __dealloc__(self):
        ut_free_system(self.csystem)


cdef class Unit:
    cdef ut_unit *cunit

    def __cinit__(self):
        self.cunit = NULL

    def __dealloc__(self):
        ut_free(self.cunit)


cdef class Converter:
    cdef cv_converter *cconverter

    def __cinit__(self):
        self.cconverter = NULL

    def __dealloc__(self):
        cv_free(self.cconverter)


cdef class ErrorMessageHandler:
    cdef ut_error_message_handler chandler

    def __cinit__(self):
        self.chandler = NULL


cdef System wrap_system(ut_system* csystem):
    if csystem is NULL:
        _raise_error()
    cdef System sytem = System()
    sytem.csystem = csystem
    return sytem

cdef Unit wrap_unit(ut_unit* cunit):
    if cunit is NULL:
        _raise_error()
    cdef Unit unit = Unit()
    unit.cunit = cunit
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
NULL_UNIT=Unit()


##### Exception class #####

class UdunitsError(Exception):
    def __init__(self, ut_status status, int errnum):
        self.status = status
        self.errnum = errnum

    def status_msg(self):
        if 0 <= self.status < len(_UT_STATUS):
            return _UT_STATUS[self.status]
        else:
            return 'UNKNOWN'

    def error_msg(self):
        return string.strerror(self.errnum) if self.errnum else ''
        

def _raise_error():
    errnum = errno.errno
    errno.errno = 0
    status = ut_get_status()
    raise UdunitsError(status, errnum)


##### Wrapper methods #####

def read_xml(char* path=NULL):
    cdef ut_system* csystem = ut_read_xml(path)
    return wrap_system(csystem)

def get_unit_by_name(System system, char* name):
    cdef ut_unit* cunit = ut_get_unit_by_name(system.csystem, name)
    return wrap_unit(cunit)

def clone(Unit unit):
    cdef ut_unit* cunit = ut_clone(unit.cunit)
    return wrap_unit(cunit)

def is_dimensionless(Unit unit):
    return ut_is_dimensionless(unit.cunit)

def compare(Unit unit1, Unit unit2):
    return ut_compare(unit1.cunit, unit2.cunit)

def are_convertible(Unit unit1, Unit unit2):
    return <bint>ut_are_convertible(unit1.cunit, unit2.cunit)

def get_converter(Unit fr, Unit to):
    cdef cv_converter* cconverter = ut_get_converter(fr.cunit, to.cunit)
    return wrap_converter(cconverter)

def scale(double factor, Unit unit):
    cdef ut_unit* cunit = ut_scale(factor, unit.cunit)
    return wrap_unit(cunit)

def offset(Unit unit, double offset):
    cdef ut_unit* cunit = ut_offset(unit.cunit, offset)
    return wrap_unit(cunit)

def offset_by_time(Unit unit, double origin):
    cdef ut_unit* cunit = ut_offset_by_time(unit.cunit, origin)
    return wrap_unit(cunit)

def multiply(Unit unit1, Unit unit2):
    cdef ut_unit* cunit = ut_multiply(unit1.cunit, unit2.cunit)
    return wrap_unit(cunit)

def invert(Unit unit):
    cdef ut_unit* cunit =  ut_invert(unit.cunit)
    return wrap_unit(cunit)

def divide(Unit numer, Unit denom):
    cdef ut_unit* cunit = ut_divide(numer.cunit, denom.cunit)
    return wrap_unit(cunit)

def raise_(Unit unit, int power):
    cdef ut_unit* cunit = ut_raise(unit.cunit, power)
    return wrap_unit(cunit)

def root(Unit unit, int root):
    cdef ut_unit* cunit = ut_root(unit.cunit, root)
    return wrap_unit(cunit)

def log(double base, Unit reference):
    cdef ut_unit* cunit = ut_log(base, reference.cunit)
    return wrap_unit(cunit)

def parse(System system, char* string, ut_encoding encoding):
    cdef ut_unit* cunit = ut_parse(system.csystem, string, encoding)
    return wrap_unit(cunit)

def format(Unit unit, unsigned opts=0):
    cdef bytearray buf = bytearray(_STRING_BUFFER_DEPTH)
    n = ut_format(unit.cunit, buf, len(buf), opts)
    if n > _STRING_BUFFER_DEPTH:
        buf = bytearray(n)
        n = ut_format(unit.cunit, buf, len(buf), opts)
    elif n == -1:
        _raise_error()
    return buf[:n]

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

def convert_doubles(Converter converter, np.ndarray[np.float64_t] in_, np.ndarray[np.float32_t] out):
    cv_convert_doubles(converter.cconverter, <double*> in_.data, in_.size, <double*> out.data)
    return out
