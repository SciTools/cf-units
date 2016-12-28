import numpy as np
cimport numpy as np
from libc cimport errno


##### Wrapper classes #####

# To avoid having to do None/NULL checks to convert between those two values,
# we define an is_null() convenience function for each class, to be used in
# user code.

cdef class System:
    cdef ut_system *csystem

    def __cinit__(self):
        self.csystem = NULL

    def __dealloc__(self):
        ut_free_system(self.csystem)

    def is_null(self):
        return self.csystem is NULL


cdef class Unit:
    cdef ut_unit *cunit

    def __cinit__(self):
        self.cunit = NULL

    def __dealloc__(self):
        ut_free(self.cunit)

    def is_null(self):
        return self.cunit is NULL


cdef class Converter:
    cdef cv_converter *cconverter

    def __cinit__(self):
        self.cconverter = NULL

    def __dealloc__(self):
        cv_free(self.cconverter)

    def is_null(self):
        return self.cconverter is NULL

cdef class ErrorMessageHandler:
    cdef ut_error_message_handler chandler

    def __cinit__(self):
        self.chandler = NULL

    def is_null(self):
        return self.chandler is NULL


cdef ErrorMessageHandler _ignore = ErrorMessageHandler()
_ignore.chandler = ut_ignore
ignore = _ignore


##### Wrapper methods #####

# Cython apparently resets the errno value to 0 between Python-level calls,
# so we remember the value directly after the call.
def save_errno(f):
    def inner_func(*args, **kwargs):
        global my_errno
        res = f(*args, **kwargs)
        my_errno = errno.errno
        return res
    return inner_func

@save_errno
def read_xml(char* path=NULL):
    cdef System system = System()
    system.csystem = ut_read_xml(path)
    return system

def get_unit_by_name(System system, char* name):
    cdef Unit unit = Unit()
    unit.cunit = ut_get_unit_by_name(system.csystem, name)
    return unit

@save_errno
def clone(Unit unit):
    unit_clone = Unit()
    unit_clone.cunit = ut_clone(unit.cunit)
    return unit

def is_dimensionless(Unit unit):
    return ut_is_dimensionless(unit.cunit)

def compare(Unit unit1, Unit unit2):
    return ut_compare(unit1.cunit, unit2.cunit)

def are_convertible(Unit unit1, Unit unit2):
    return ut_are_convertible(unit1.cunit, unit2.cunit)

@save_errno
def get_converter(Unit fr, Unit to):
    cdef Converter converter = Converter()
    converter.cconverter = ut_get_converter(fr.cunit, to.cunit)
    return converter

def scale(double factor, Unit unit):
    cdef Unit result = Unit()
    result.cunit = ut_scale(factor, unit.cunit)
    return result

@save_errno
def offset(Unit unit, double offset):
    cdef Unit result = Unit()
    result.cunit = ut_offset(unit.cunit, offset)
    return result

@save_errno
def offset_by_time(Unit unit, double origin):
    cdef Unit result = Unit()
    result.cunit = ut_offset_by_time(unit.cunit, origin)
    return result

@save_errno
def multiply(Unit unit1, Unit unit2):
    cdef Unit result = Unit()
    result.cunit = ut_multiply(unit1.cunit, unit2.cunit)
    return result

@save_errno
def invert(Unit unit):
    cdef Unit result = Unit()
    result.cunit = ut_invert(unit.cunit)
    return result

@save_errno
def divide(Unit numer, Unit denom):
    cdef Unit result = Unit()
    result.cunit = ut_divide(numer.cunit, denom.cunit)
    return result

@save_errno
def raise_(Unit unit, int power):
    cdef Unit result = Unit()
    result.cunit = ut_raise(unit.cunit, power)
    return result

@save_errno
def root(Unit unit, int root):
    cdef Unit result = Unit()
    result.cunit = ut_root(unit.cunit, root)
    return result

@save_errno
def log(double base, Unit reference):
    cdef Unit result = Unit()
    result.cunit = ut_log(base, reference.cunit)
    return result

@save_errno
def parse(System system, char* string, ut_encoding encoding):
    cdef Unit result = Unit()
    result.cunit = ut_parse(system.csystem, string, encoding)
    return result

def format(Unit unit, bytearray buf, unsigned opts=0):
    return ut_format(unit.cunit, buf, len(buf), opts)

def encode_date(int year, int month, int day):
    return ut_encode_date(year, month, day)

def encode_clock(int hours, int minutes, double seconds):
    return encode_clock(hours, minutes, seconds)

def encode_time(int year, int month, int day,
                int hour, int minute, double second):
    return encode_time(year, month, day, hour, minute, second)

def decode_time(double value):
    cdef int year, month, day, hour, minute
    cdef double second, resolution
    ut_decode_time(value, &year, &month, &day, &hour, &minute, &second,
                   &resolution)
    return (year, month, day, hour, minute, second, resolution)

def get_status():
    return ut_get_status()

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


##### Helpers #####

cdef int my_errno = 0

def get_errno():
    return my_errno

def set_errno(int errnum):
    global my_errno
    errno.errno = errnum
    my_errno = errnum
