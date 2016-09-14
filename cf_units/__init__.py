# (C) British Crown Copyright 2015 - 2016, Met Office
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

Provision of a wrapper class to support Unidata/UCAR UDUNITS-2, and the
netcdftime calendar functionality.

See also: `UDUNITS-2
<http://www.unidata.ucar.edu/software/udunits/udunits-2/udunits2.html>`_.

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import six

from contextlib import contextmanager
import copy
import ctypes
import ctypes.util
import os.path
import sys
import warnings

import netcdftime
import numpy as np

from . import config
from .util import _OrderedHashable, approx_equal

# Define __version__ based on versioneer's interpretation.
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['CALENDAR_STANDARD',
           'CALENDAR_GREGORIAN',
           'CALENDAR_PROLEPTIC_GREGORIAN',
           'CALENDAR_NO_LEAP',
           'CALENDAR_JULIAN',
           'CALENDAR_ALL_LEAP',
           'CALENDAR_365_DAY',
           'CALENDAR_366_DAY',
           'CALENDAR_360_DAY',
           'CALENDARS',
           'UT_NAMES',
           'UT_DEFINITION',
           'UT_ASCII',
           'FLOAT32',
           'FLOAT64',
           'julian_day2date',
           'date2julian_day',
           'is_time',
           'is_vertical',
           'Unit',
           'date2num',
           'decode_time',
           'encode_clock',
           'encode_date',
           'encode_time',
           'num2date',
           'suppress_errors']


########################################################################
#
# module level constants
#
########################################################################

#
# default constants
#
EPOCH = '1970-01-01 00:00:00'
_STRING_BUFFER_DEPTH = 128
_UNKNOWN_UNIT_STRING = 'unknown'
_UNKNOWN_UNIT_SYMBOL = '?'
_UNKNOWN_UNIT = [_UNKNOWN_UNIT_STRING, _UNKNOWN_UNIT_SYMBOL, '???', '']
_NO_UNIT_STRING = 'no_unit'
_NO_UNIT_SYMBOL = '-'
_NO_UNIT = [_NO_UNIT_STRING, _NO_UNIT_SYMBOL, 'no unit', 'no-unit', 'nounit']
_UNIT_DIMENSIONLESS = '1'
_OP_SINCE = ' since '
_CATEGORY_UNKNOWN, _CATEGORY_NO_UNIT, _CATEGORY_UDUNIT = range(3)


#
# libudunits2 constants
#
# ut_status enumerations
_UT_STATUS = ['UT_SUCCESS', 'UT_BAD_ARG', 'UT_EXISTS', 'UT_NO_UNIT',
              'UT_OS', 'UT_NOT_SAME_NAME', 'UT_MEANINGLESS', 'UT_NO_SECOND',
              'UT_VISIT_ERROR', 'UT_CANT_FORMAT', 'UT_SYNTAX', 'UT_UNKNOWN',
              'UT_OPEN_ARG', 'UT_OPEN_ENV', 'UT_OPEN_DEFAULT', 'UT_PARSE']

# explicit function names
_UT_HANDLER = 'ut_set_error_message_handler'
_UT_IGNORE = 'ut_ignore'

# ut_encoding enumerations
UT_ASCII = 0
UT_ISO_8859_1 = 1
UT_LATIN1 = 1
UT_UTF8 = 2
UT_NAMES = 4
UT_DEFINITION = 8

UT_FORMATS = [UT_ASCII, UT_ISO_8859_1, UT_LATIN1, UT_UTF8, UT_NAMES,
              UT_DEFINITION]

#
# netcdftime constants
#
CALENDAR_STANDARD = 'standard'
CALENDAR_GREGORIAN = 'gregorian'
CALENDAR_PROLEPTIC_GREGORIAN = 'proleptic_gregorian'
CALENDAR_NO_LEAP = 'noleap'
CALENDAR_JULIAN = 'julian'
CALENDAR_ALL_LEAP = 'all_leap'
CALENDAR_365_DAY = '365_day'
CALENDAR_366_DAY = '366_day'
CALENDAR_360_DAY = '360_day'

CALENDARS = [CALENDAR_STANDARD, CALENDAR_GREGORIAN,
             CALENDAR_PROLEPTIC_GREGORIAN, CALENDAR_NO_LEAP, CALENDAR_JULIAN,
             CALENDAR_ALL_LEAP, CALENDAR_365_DAY, CALENDAR_366_DAY,
             CALENDAR_360_DAY]

#
# ctypes types
#
FLOAT32 = ctypes.c_float
FLOAT64 = ctypes.c_double

########################################################################
#
# module level variables
#
########################################################################

# cache for ctypes foreign shared library handles
_lib_c = None
_lib_ud = None
_ud_system = None

# cache for libc shared library functions
_strerror = None

# class cache for libudunits2 shared library functions
_cv_convert_float = None
_cv_convert_floats = None
_cv_convert_double = None
_cv_convert_doubles = None
_cv_free = None
_ut_are_convertible = None
_ut_clone = None
_ut_compare = None
_ut_decode_time = None
_ut_divide = None
_ut_encode_clock = None
_ut_encode_date = None
_ut_encode_time = None
_ut_format = None
_ut_free = None
_ut_get_converter = None
_ut_get_status = None
_ut_get_unit_by_name = None
_ut_ignore = None
_ut_invert = None
_ut_is_dimensionless = None
_ut_log = None
_ut_multiply = None
_ut_offset = None
_ut_offset_by_time = None
_ut_parse = None
_ut_raise = None
_ut_read_xml = None
_ut_root = None
_ut_scale = None
_ut_set_error_message_handler = None

########################################################################
#
# module level statements
#
########################################################################

#
# load the libc shared library
#
if _lib_c is None:
    if sys.platform == 'win32':
        _lib_c = ctypes.cdll.msvcrt
    else:
        _lib_c = ctypes.CDLL(ctypes.util.find_library('libc'))

    #
    # cache common shared library functions
    #
    _strerror = _lib_c.strerror
    _strerror.restype = ctypes.c_char_p

#
# load the libudunits2 shared library
#
if _lib_ud is None:
    _udunits2_c = config.get_option(
        'System', 'udunits2_path',
        default=ctypes.util.find_library('udunits2'))
    if _udunits2_c:
        _lib_ud = ctypes.CDLL(_udunits2_c, use_errno=True)
    else:
        msg = ('Could not find the udunits2 library "{}."'
               ' You may need to install udunits2.').format
        raise OSError(msg(_udunits2_c))

    #
    # cache common shared library functions
    #
    _cv_convert_float = _lib_ud.cv_convert_float
    _cv_convert_float.argtypes = [ctypes.c_void_p, ctypes.c_float]
    _cv_convert_float.restype = ctypes.c_float

    _cv_convert_floats = _lib_ud.cv_convert_floats
    _cv_convert_floats.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                   ctypes.c_ulong, ctypes.c_void_p]
    _cv_convert_floats.restype = ctypes.c_void_p

    _cv_convert_double = _lib_ud.cv_convert_double
    _cv_convert_double.argtypes = [ctypes.c_void_p, ctypes.c_double]
    _cv_convert_double.restype = ctypes.c_double

    _cv_convert_doubles = _lib_ud.cv_convert_doubles
    _cv_convert_doubles.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                    ctypes.c_ulong, ctypes.c_void_p]
    _cv_convert_doubles.restype = ctypes.c_void_p

    _cv_free = _lib_ud.cv_free
    _cv_free.argtypes = [ctypes.c_void_p]

    _ut_are_convertible = _lib_ud.ut_are_convertible
    _ut_are_convertible.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    _ut_clone = _lib_ud.ut_clone
    _ut_clone.argtypes = [ctypes.c_void_p]
    _ut_clone.restype = ctypes.c_void_p

    _ut_compare = _lib_ud.ut_compare
    _ut_compare.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _ut_compare.restype = ctypes.c_int

    _ut_decode_time = _lib_ud.ut_decode_time
    _ut_decode_time.restype = None

    _ut_divide = _lib_ud.ut_divide
    _ut_divide.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _ut_divide.restype = ctypes.c_void_p

    _ut_encode_clock = _lib_ud.ut_encode_clock
    _ut_encode_clock.restype = ctypes.c_double

    _ut_encode_date = _lib_ud.ut_encode_date
    _ut_encode_date.restype = ctypes.c_double

    _ut_encode_time = _lib_ud.ut_encode_time
    _ut_encode_time.restype = ctypes.c_double

    _ut_format = _lib_ud.ut_format
    _ut_format.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                           ctypes.c_ulong, ctypes.c_uint]

    _ut_free = _lib_ud.ut_free
    _ut_free.argtypes = [ctypes.c_void_p]
    _ut_free.restype = None

    _ut_get_converter = _lib_ud.ut_get_converter
    _ut_get_converter.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _ut_get_converter.restype = ctypes.c_void_p

    _ut_get_status = _lib_ud.ut_get_status

    _ut_get_unit_by_name = _lib_ud.ut_get_unit_by_name
    _ut_get_unit_by_name.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _ut_get_unit_by_name.restype = ctypes.c_void_p

    _ut_invert = _lib_ud.ut_invert
    _ut_invert.argtypes = [ctypes.c_void_p]
    _ut_invert.restype = ctypes.c_void_p

    _ut_is_dimensionless = _lib_ud.ut_is_dimensionless
    _ut_is_dimensionless.argtypes = [ctypes.c_void_p]

    _ut_log = _lib_ud.ut_log
    _ut_log.argtypes = [ctypes.c_double, ctypes.c_void_p]
    _ut_log.restype = ctypes.c_void_p

    _ut_multiply = _lib_ud.ut_multiply
    _ut_multiply.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _ut_multiply.restype = ctypes.c_void_p

    _ut_offset = _lib_ud.ut_offset
    _ut_offset.argtypes = [ctypes.c_void_p, ctypes.c_double]
    _ut_offset.restype = ctypes.c_void_p

    _ut_offset_by_time = _lib_ud.ut_offset_by_time
    _ut_offset_by_time.argtypes = [ctypes.c_void_p, ctypes.c_double]
    _ut_offset_by_time.restype = ctypes.c_void_p

    _ut_parse = _lib_ud.ut_parse
    _ut_parse.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    _ut_parse.restype = ctypes.c_void_p

    _ut_raise = _lib_ud.ut_raise
    _ut_raise.argtypes = [ctypes.c_void_p, ctypes.c_int]
    _ut_raise.restype = ctypes.c_void_p

    _ut_read_xml = _lib_ud.ut_read_xml
    _ut_read_xml.argtypes = [ctypes.c_char_p]
    _ut_read_xml.restype = ctypes.c_void_p

    _ut_root = _lib_ud.ut_root
    _ut_root.argtypes = [ctypes.c_void_p, ctypes.c_int]
    _ut_root.restype = ctypes.c_void_p

    _ut_scale = _lib_ud.ut_scale
    _ut_scale.argtypes = [ctypes.c_double, ctypes.c_void_p]
    _ut_scale.restype = ctypes.c_void_p

    # Convenience dictionary for the Unit convert method.
    _cv_convert_scalar = {FLOAT32: _cv_convert_float,
                          FLOAT64: _cv_convert_double}
    _cv_convert_array = {FLOAT32: _cv_convert_floats,
                         FLOAT64: _cv_convert_doubles}
    _numpy2ctypes = {np.float32: FLOAT32, np.float64: FLOAT64}
    _ctypes2numpy = {v: k for k, v in _numpy2ctypes.items()}


@contextmanager
def suppress_errors():
    """
    Suppresses all error messages from UDUNITS-2.

    """
    _func_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p,
                                  use_errno=True)
    _set_handler_type = ctypes.CFUNCTYPE(_func_type, _func_type)
    _ut_set_error_message_handler = _set_handler_type((_UT_HANDLER, _lib_ud))
    _ut_ignore = _func_type((_UT_IGNORE, _lib_ud))
    _default_handler = _ut_set_error_message_handler(_ut_ignore)
    try:
        yield
    finally:
        _ut_set_error_message_handler(_default_handler)


#
# load the UDUNITS-2 xml-formatted unit-database
#
if not _ud_system:
    # Ignore standard noisy UDUNITS-2 start-up.
    with suppress_errors():
        # Load the unit-database from the default location (modified via
        # the UDUNITS2_XML_PATH environment variable) and if that fails look
        # relative to sys.prefix to support environments such as conda.
        _ud_system = _ut_read_xml(None)
        if _ud_system is None:
            _alt_xml_path = config.get_option(
                'System', 'udunits2_xml_path',
                default=os.path.join(sys.prefix, 'share', 'udunits',
                                     'udunits2.xml'))
            _ud_system = _ut_read_xml(_alt_xml_path.encode())
    if not _ud_system:
        _status_msg = 'UNKNOWN'
        _error_msg = ''
        _status = _ut_get_status()
        try:
            _status_msg = _UT_STATUS[_status]
        except IndexError:
            pass
        _errno = ctypes.get_errno()
        if _errno != 0:
            _error_msg = ': "%s"' % _strerror(_errno)
            ctypes.set_errno(0)
        raise OSError('[%s] Failed to open UDUNITS-2 XML unit database %s' % (
            _status_msg, _error_msg))


########################################################################
#
# module level function definitions
#
########################################################################

def encode_time(year, month, day, hour, minute, second):
    """
    Return date/clock time encoded as a double precision value.

    Encoding performed using UDUNITS-2 hybrid Gregorian/Julian calendar.
    Dates on or after 1582-10-15 are assumed to be Gregorian dates;
    dates before that are assumed to be Julian dates. In particular, the
    year 1 BCE is immediately followed by the year 1 CE.

    Args:

    * year (int):
        Year value to be encoded.
    * month (int):
        Month value to be encoded.
    * day (int):
        Day value to be encoded.
    * hour (int):
        Hour value to be encoded.
    * minute (int):
        Minute value to be encoded.
    * second (int):
        Second value to be encoded.

    Returns:
        float.

    For example:

        >>> import cf_units
        >>> cf_units.encode_time(1970, 1, 1, 0, 0, 0)
        -978307200.0

    """

    return _ut_encode_time(ctypes.c_int(year), ctypes.c_int(month),
                           ctypes.c_int(day), ctypes.c_int(hour),
                           ctypes.c_int(minute), ctypes.c_double(second))


def encode_date(year, month, day):
    """
    Return date encoded as a double precision value.

    Encoding performed using UDUNITS-2 hybrid Gergorian/Julian calendar.
    Dates on or after 1582-10-15 are assumed to be Gregorian dates;
    dates before that are assumed to be Julian dates. In particular, the
    year 1 BCE is immediately followed by the year 1 CE.

    Args:

    * year (int):
        Year value to be encoded.
    * month (int):
        Month value to be encoded.
    * day (int):
        Day value to be encoded.

    Returns:
        float.

    For example:

        >>> import cf_units
        >>> cf_units.encode_date(1970, 1, 1)
        -978307200.0

    """

    return _ut_encode_date(ctypes.c_int(year), ctypes.c_int(month),
                           ctypes.c_int(day))


def encode_clock(hour, minute, second):
    """
    Return clock time encoded as a double precision value.

    Args:

    * hour (int):
        Hour value to be encoded.
    * minute (int):
        Minute value to be encoded.
    * second (int):
        Second value to be encoded.

    Returns:
        float.

    For example:

        >>> import cf_units
        >>> cf_units.encode_clock(0, 0, 0)
        0.0

    """

    return _ut_encode_clock(ctypes.c_int(hour), ctypes.c_int(minute),
                            ctypes.c_double(second))


def decode_time(time):
    """
    Decode a double precision date/clock time value into its component
    parts and return as tuple.

    Decode time into it's year, month, day, hour, minute, second, and
    resolution component parts. Where resolution is the uncertainty of
    the time in seconds.

    Args:

    * time (float): Date/clock time encoded as a double precision value.

    Returns:
        tuple of (year, month, day, hour, minute, second, resolution).

    For example:

        >>> import cf_units
        >>> cf_units.decode_time(cf_units.encode_time(1970, 1, 1, 0, 0, 0))
        (1970, 1, 1, 0, 0, 0.0, 1.086139178596568e-07)

    """

    year = ctypes.c_int()
    month = ctypes.c_int()
    day = ctypes.c_int()
    hour = ctypes.c_int()
    minute = ctypes.c_int()
    second = ctypes.c_double()
    resolution = ctypes.c_double()
    _ut_decode_time(ctypes.c_double(time), ctypes.pointer(year),
                    ctypes.pointer(month), ctypes.pointer(day),
                    ctypes.pointer(hour), ctypes.pointer(minute),
                    ctypes.pointer(second), ctypes.pointer(resolution))
    return (year.value, month.value, day.value, hour.value, minute.value,
            second.value, resolution.value)


def julian_day2date(julian_day, calendar):
    """
    Return a netcdftime datetime-like object representing the Julian day.

    If calendar is 'standard' or 'gregorian', Julian day follows
    Julian calendar on and before 1582-10-5, Gregorian calendar after
    1582-10-15.
    If calendar is 'proleptic_gregorian', Julian Day follows Gregorian
    calendar.
    If calendar is 'julian', Julian Day follows Julian calendar.

    The datetime object is a 'real' datetime object if the date falls in
    the Gregorian calendar (i.e. calendar is 'proleptic_gregorian', or
    calendar is 'standard'/'gregorian' and the date is after 1582-10-15).
    Otherwise, it's a 'phony' datetime object which is actually an instance
    of netcdftime.datetime.

    Algorithm:
        Meeus, Jean (1998) Astronomical Algorithms (2nd Edition).
        Willmann-Bell, Virginia. p. 63.

    Args:

    * julian_day (float):
        Julian day with a resolution of 1 second.
    * calendar (string):
        Name of the calendar, see cf_units.CALENDARS.

    Returns:
        datetime or netcdftime.datetime.

    For example:

        >>> import cf_units
        >>> import datetime
        >>> cf_units.julian_day2date(
        ...    cf_units.date2julian_day(datetime.datetime(1970, 1, 1, 0, 0, 0),
        ...                             cf_units.CALENDAR_STANDARD),
        ...     cf_units.CALENDAR_STANDARD)
        datetime.datetime(1970, 1, 1, 0, 0)

    """

    return netcdftime.DateFromJulianDay(julian_day, calendar)


def date2julian_day(date, calendar):
    """
    Return the Julian day (resolution of 1 second) from a netcdftime
    datetime-like object.

    If calendar is 'standard' or 'gregorian', Julian day follows Julian
    calendar on and before 1582-10-5, Gregorian calendar after 1582-10-15.
    If calendar is 'proleptic_gregorian', Julian day follows Gregorian
    calendar.
    If calendar is 'julian', Julian day follows Julian calendar.

    Algorithm:
        Meeus, Jean (1998) Astronomical Algorithms (2nd Edition).
        Willmann-Bell, Virginia. p. 63.

    Args:

    * date (netcdftime.date):
        Date and time representation.
    * calendar (string):
        Name of the calendar, see cf_units.CALENDARS.

    Returns:
        float.

    For example:

        >>> import cf_units
        >>> import datetime
        >>> cf_units.date2julian_day(datetime.datetime(1970, 1, 1, 0, 0, 0),
        ...                          cf_units.CALENDAR_STANDARD)
        2440587.5

    """

    return netcdftime.JulianDayFromDate(date, calendar)


def date2num(date, unit, calendar):
    """
    Return numeric time value (resolution of 1 second) encoding of
    datetime object.

    The units of the numeric time values are described by the unit and
    calendar arguments. The datetime objects must be in UTC with no
    time-zone offset. If there is a time-zone offset in unit, it will be
    applied to the returned numeric values.

    Like the :func:`matplotlib.dates.date2num` function, except that it allows
    for different units and calendars.  Behaves the same as if
    unit = 'days since 0001-01-01 00:00:00' and
    calendar = 'proleptic_gregorian'.

    Args:

    * date (datetime):
        A datetime object or a sequence of datetime objects.
        The datetime objects should not include a time-zone offset.
    * unit (string):
        A string of the form '<time-unit> since <time-origin>' describing
        the time units. The <time-unit> can be days, hours, minutes or seconds.
        The <time-origin> is a date/time reference point. A valid choice
        would be unit='hours since 1800-01-01 00:00:00 -6:00'.
    * calendar (string):
        Name of the calendar, see cf_units.CALENDARS.

    Returns:
        float, or numpy.ndarray of float.

    For example:

        >>> import cf_units
        >>> import datetime
        >>> dt1 = datetime.datetime(1970, 1, 1, 6, 0, 0)
        >>> dt2 = datetime.datetime(1970, 1, 1, 7, 0, 0)
        >>> cf_units.date2num(dt1, 'hours since 1970-01-01 00:00:00',
        ...               cf_units.CALENDAR_STANDARD)
        6.0
        >>> cf_units.date2num([dt1, dt2], 'hours since 1970-01-01 00:00:00',
        ...               cf_units.CALENDAR_STANDARD)
        array([ 6.,  7.])

    """

    #
    # ensure to strip out any 'UTC' postfix which is generated by
    # UDUNITS-2 formatted output and causes the netcdftime parser
    # to choke
    #
    unit_string = unit.rstrip(" UTC")
    if unit_string.endswith(" since epoch"):
        unit_string = unit_string.replace("epoch", EPOCH)
    cdftime = netcdftime.utime(unit_string, calendar=calendar)
    date = _discard_microsecond(date)
    return cdftime.date2num(date)


def _discard_microsecond(date):
    """
    Return a date with the microsecond componenet discarded.

    Works for scalars, sequences and numpy arrays. Returns a scalar
    if input is a scalar, else returns a numpy array.

    Args:

    * date (datetime.datetime or netcdftime.datetime):
        Date value/s

    Returns:
        datetime, or list of datetime object.

    """
    is_scalar = False
    if not hasattr(date, '__iter__'):
        date = [date]
        is_scalar = True
    dates = [d.__class__(d.year, d.month, d.day, d.hour, d.minute, d.second)
             for d in date]
    return dates[0] if is_scalar else dates


def num2date(time_value, unit, calendar):
    """
    Return datetime encoding of numeric time value (resolution of 1 second).

    The units of the numeric time value are described by the unit and
    calendar arguments. The returned datetime object represent UTC with
    no time-zone offset, even if the specified unit contain a time-zone
    offset.

    Like the :func:`matplotlib.dates.num2date` function, except that it allows
    for different units and calendars.  Behaves the same if
    unit = 'days since 001-01-01 00:00:00'}
    calendar = 'proleptic_gregorian'.

    The datetime instances returned are 'real' python datetime
    objects if the date falls in the Gregorian calendar (i.e.
    calendar='proleptic_gregorian', or calendar = 'standard' or 'gregorian'
    and the date is after 1582-10-15). Otherwise, they are 'phony' datetime
    objects which support some but not all the methods of 'real' python
    datetime objects.  This is because the python datetime module cannot
    use the 'proleptic_gregorian' calendar, even before the switch
    occured from the Julian calendar in 1582. The datetime instances
    do not contain a time-zone offset, even if the specified unit
    contains one.

    Works for scalars, sequences and numpy arrays. Returns a scalar
    if input is a scalar, else returns a numpy array.

    Args:

    * time_value (float):
        Numeric time value/s. Maximum resolution is 1 second.
    * unit (sting):
        A string of the form '<time-unit> since <time-origin>'
        describing the time units. The <time-unit> can be days, hours,
        minutes or seconds. The <time-origin> is the date/time reference
        point. A valid choice would be
        unit='hours since 1800-01-01 00:00:00 -6:00'.
    * calendar (string):
        Name of the calendar, see cf_units.CALENDARS.

    Returns:
        datetime, or numpy.ndarray of datetime object.

    For example:

        >>> import cf_units
        >>> import datetime
        >>> cf_units.num2date(6, 'hours since 1970-01-01 00:00:00',
        ...                   cf_units.CALENDAR_STANDARD)
        datetime.datetime(1970, 1, 1, 6, 0)
        >>> cf_units.num2date([6, 7], 'hours since 1970-01-01 00:00:00',
        ...                   cf_units.CALENDAR_STANDARD)
        array([datetime.datetime(1970, 1, 1, 6, 0),
               datetime.datetime(1970, 1, 1, 7, 0)], dtype=object)

    """

    #
    # ensure to strip out any 'UTC' postfix which is generated by
    # UDUNITS-2 formatted output and causes the netcdftime parser
    # to choke
    #
    unit_string = unit.rstrip(" UTC")
    if unit_string.endswith(" since epoch"):
        unit_string = unit_string.replace("epoch", EPOCH)
    cdftime = netcdftime.utime(unit_string, calendar=calendar)
    return _num2date_to_nearest_second(time_value, cdftime)


def _num2date_to_nearest_second(time_value, utime):
    """
    Return datetime encoding of numeric time value with respect to the given
    time reference units, with a resolution of 1 second.

    * time_value (float):
        Numeric time value/s.
    * utime (netcdftime.utime):
        netcdf.utime object with which to perform the conversion/s.

    Returns:
        datetime, or numpy.ndarray of datetime object.
    """
    is_scalar = False
    if not hasattr(time_value, '__iter__'):
        time_value = [time_value]
        is_scalar = True
    time_values = np.array(list(time_value))

    # We account for the edge case where the time is in seconds and has a
    # half second: utime.num2date() may produce a date that would round
    # down.
    #
    # Note that this behaviour is different to the num2date function in older
    # versions of netcdftime that didn't have microsecond precision. In those
    # versions, a half-second value would be rounded up or down arbitrarily. It
    # is probably not possible to replicate that behaviour with the current
    # version (1.4.1), if one wished to do so for the sake of consistency.
    has_half_seconds = np.logical_and(utime.units == 'seconds',
                                      time_values % 1. == 0.5)
    dates = utime.num2date(time_values)
    try:
        # We can assume all or none of the dates have a microsecond attribute
        microseconds = np.array([d.microsecond for d in dates])
    except AttributeError:
        microseconds = 0
    round_mask = np.logical_or(has_half_seconds, microseconds != 0)
    ceil_mask = np.logical_or(has_half_seconds, microseconds >= 500000)
    if time_values[ceil_mask].size > 0:
        useconds = Unit('second')
        second_frac = useconds.convert(0.75, utime.units)
        dates[ceil_mask] = utime.num2date(time_values[ceil_mask] + second_frac)
    # Create date objects of the same type returned by utime.num2date()
    # (either datetime.datetime or netcdftime.datetime), discarding the
    # microseconds
    dates[round_mask] = _discard_microsecond(dates[round_mask])

    return dates[0] if is_scalar else dates


########################################################################
#
# unit wrapper class for unidata/ucar UDUNITS-2
#
########################################################################

def _Unit(category, ut_unit, calendar=None, origin=None):
    unit = _OrderedHashable.__new__(Unit)
    unit._init(category, ut_unit, calendar, origin)
    return unit


_CACHE = {}


def as_unit(unit):
    """
    Returns a Unit corresponding to the given unit.

    .. note::

        If the given unit is already a Unit it will be returned unchanged.

    """
    if isinstance(unit, Unit):
        result = unit
    else:
        result = None
        use_cache = isinstance(unit, six.string_types) or unit is None
        if use_cache:
            result = _CACHE.get(unit)
        if result is None:
            # Typically unit is a string, however we cater for other types of
            # 'unit' (e.g. iris.unit.Unit).
            result = Unit(unit, calendar=getattr(unit, 'calendar', None))
            if use_cache:
                _CACHE[unit] = result
    return result


def is_time(unit):
    """
    Determine whether the unit is a related SI Unit of time.

    Args:

    * unit (string/Unit): Unit to be compared.

    Returns:
        Boolean.

    For example:

        >>> import cf_units
        >>> cf_units.is_time('hours')
        True
        >>> cf_units.is_time('meters')
        False

    """
    return as_unit(unit).is_time()


def is_vertical(unit):
    """
    Determine whether the unit is a related SI Unit of pressure or distance.

    Args:

    * unit (string/Unit): Unit to be compared.

    Returns:
        Boolean.

    For example:

        >>> import cf_units
        >>> cf_units.is_vertical('millibar')
        True
        >>> cf_units.is_vertical('km')
        True

    """
    return as_unit(unit).is_vertical()


class Unit(_OrderedHashable):
    """
    A class to represent S.I. units and support common operations to
    manipulate such units in a consistent manner as per UDUNITS-2.

    These operations include scaling the unit, offsetting the unit by a
    constant or time, inverting the unit, raising the unit by a power,
    taking a root of the unit, taking a log of the unit, multiplying the
    unit by a constant or another unit, dividing the unit by a constant
    or another unit, comparing units, copying units and converting unit
    data to single precision or double precision floating point numbers.

    This class also supports time and calendar defintion and manipulation.

    """
    def _init_from_tuple(self, values):
        for name, value in zip(self._names, values):
            object.__setattr__(self, name, value)

    def _as_tuple(self):
        return tuple(getattr(self, name) for name in self._names)

    # Provide hash semantics

    def _identity(self):
        return self._as_tuple()

    def __hash__(self):
        return hash(self._identity())

    # Provide default ordering semantics

    def __lt__(self, other):
        return self._identity() < other._identity()

    # Prevent attribute updates

    def __setattr__(self, name, value):
        raise AttributeError('Instances of %s are immutable' %
                             type(self).__name__)

    def __delattr__(self, name):
        raise AttributeError('Instances of %s are immutable' %
                             type(self).__name__)

    # Declare the attribute names relevant to the ordered and hashable
    #  behaviour.
    _names = ('category', 'ut_unit', 'calendar', 'origin')

    category = None
    'Is this an unknown unit, a no-unit, or a UDUNITS-2 unit.'

    ut_unit = None
    'Reference to the ctypes quantity defining the UDUNITS-2 unit.'

    calendar = None
    'Represents the unit calendar name, see cf_units.CALENDARS'

    origin = None
    'The original string used to create this unit.'

    __slots__ = ()

    def __init__(self, unit, calendar=None):
        """
        Create a wrapper instance for UDUNITS-2.

        An optional calendar may be provided for a unit which defines a
        time reference of the form '<time-unit> since <time-origin>'
        i.e. unit='days since 1970-01-01 00:00:00'. For a unit that is a
        time reference, the default calendar is 'standard'.

        Accepted calendars are as follows,

        * 'standard' or 'gregorian' - Mixed Gregorian/Julian calendar as
          defined by udunits.
        * 'proleptic_gregorian' - A Gregorian calendar extended to dates
          before 1582-10-15. A year is a leap year if either,

            1. It is divisible by 4 but not by 100, or
            2. It is divisible by 400.

        * 'noleap' or '365_day' - A Gregorian calendar without leap
          years i.e. all years are 365 days long.
        * 'all_leap' or '366_day' - A Gregorian calendar with every year
          being a leap year i.e. all years are 366 days long.
        * '360_day' - All years are 360 days divided into 30 day months.
        * 'julian' - Proleptic Julian calendar, extended to dates after
          1582-10-5. A year is a leap year if it is divisible by 4.

        Args:

        * unit:
            Specify the unit as defined by UDUNITS-2.
        * calendar (string):
            Describes the calendar used in time calculations. The
            default is 'standard' or 'gregorian' for a time reference
            unit.

        Returns:

            Unit object.

        Units should be set to "no_unit" for values which are strings.
        Units can also be set to "unknown" (or None).
        For example:

            >>> from cf_units import Unit
            >>> volts = Unit('volts')
            >>> no_unit = Unit('no_unit')
            >>> unknown = Unit('unknown')
            >>> unknown = Unit(None)

        """
        ut_unit = None
        calendar_ = None

        if unit is None:
            unit = ''
        else:
            unit = str(unit).strip()

        if unit.lower().endswith(' utc'):
            unit = unit[:unit.lower().rfind(' utc')]

        if unit.endswith(" since epoch"):
            unit = unit.replace("epoch", EPOCH)

        if unit.lower() in _UNKNOWN_UNIT:
            # TODO - removing the option of an unknown unit. Currently
            # the auto generated MOSIG rules are missing units on a
            # number of phenomena which would lead to errors.
            # Will be addressed by work on metadata translation.
            category = _CATEGORY_UNKNOWN
            unit = _UNKNOWN_UNIT_STRING
        elif unit.lower() in _NO_UNIT:
            category = _CATEGORY_NO_UNIT
            unit = _NO_UNIT_STRING
        else:
            category = _CATEGORY_UDUNIT
            ut_unit = _ut_parse(_ud_system, unit.encode('ascii'), UT_ASCII)
            # _ut_parse returns 0 on failure
            if ut_unit is None:
                self._raise_error('Failed to parse unit "%s"' % unit)
            if _OP_SINCE in unit.lower():
                if calendar is None:
                    calendar_ = CALENDAR_GREGORIAN
                elif isinstance(calendar, six.string_types):
                    if calendar.lower() in CALENDARS:
                        calendar_ = calendar.lower()
                    else:
                        msg = '{!r} is an unsupported calendar.'
                        raise ValueError(msg.format(calendar))
                else:
                    msg = 'Expected string-like calendar argument, got {!r}.'
                    raise TypeError(msg.format(type(calendar)))

        self._init_from_tuple((category, ut_unit, calendar_, unit,))

    def _raise_error(self, msg):
        """
        Retrieve the UDUNITS-2 ut_status, the implementation-defined string
        corresponding to UDUNITS-2 errno and raise generic exception.

        """
        status_msg = 'UNKNOWN'
        error_msg = ''
        if _lib_ud:
            status = _ut_get_status()
            try:
                status_msg = _UT_STATUS[status]
            except IndexError:
                pass
            errno = ctypes.get_errno()
            if errno != 0:
                error_msg = ': "%s"' % _strerror(errno)
                ctypes.set_errno(0)

        raise ValueError('[%s] %s %s' % (status_msg, msg, error_msg))

    # NOTE:
    # "__getstate__" and "__setstate__" functions are defined here to
    # provide a custom interface for Pickle
    #  : Pickle "normal" behaviour is just to save/reinstate the object
    #    dictionary
    #  : that won't work here, because the "ut_unit" attribute is an
    #    object handle
    #    - the corresponding udunits object only exists in the original
    #      invocation
    def __getstate__(self):
        # state capture method for Pickle.dump()
        #  - return the instance data needed to reconstruct a Unit value
        return {'unit_text': self.origin, 'calendar': self.calendar}

    def __setstate__(self, state):
        # object reconstruction method for Pickle.load()
        # intercept the Pickle.load() operation and call own __init__ again
        #  - this is to ensure a valid ut_unit attribute (as these
        #    handles aren't persistent)
        self.__init__(state['unit_text'], calendar=state['calendar'])

    def __del__(self):
        # NB. If Python is terminating then the module global "_ut_free"
        # may have already been deleted ... so we check before using it.
        if _ut_free:
            _ut_free(self.ut_unit)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def is_time(self):
        """
        Determine whether this unit is a related SI Unit of time.

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('hours')
            >>> u.is_time()
            True
            >>> v = cf_units.Unit('meter')
            >>> v.is_time()
            False

        """
        if self.is_unknown() or self.is_no_unit():
            result = False
        else:
            day = _ut_get_unit_by_name(_ud_system, b'day')
            result = _ut_are_convertible(self.ut_unit, day) != 0
        return result

    def is_vertical(self):
        """
        Determine whether the unit is a related SI Unit of pressure or
        distance.

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('millibar')
            >>> u.is_vertical()
            True
            >>> v = cf_units.Unit('km')
            >>> v.is_vertical()
            True

        """
        if self.is_unknown() or self.is_no_unit():
            result = False
        else:
            bar = _ut_get_unit_by_name(_ud_system, b'bar')
            result = _ut_are_convertible(self.ut_unit, bar) != 0
            if not result:
                meter = _ut_get_unit_by_name(_ud_system, b'meter')
                result = _ut_are_convertible(self.ut_unit, meter) != 0
        return result

    def is_udunits(self):
        """Return whether the unit is a vaild unit of UDUNITS."""
        return self.ut_unit is not None

    def is_time_reference(self):
        """
        Return whether the unit is a time reference unit of the form
        '<time-unit> since <time-origin>'
        i.e. unit='days since 1970-01-01 00:00:00'

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('days since epoch')
            >>> u.is_time_reference()
            True

        """
        return self.calendar is not None

    def title(self, value):
        """
        Return the unit value as a title string.

        Args:

        * value (float): Unit value to be incorporated into title string.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('hours since epoch',
            ...                   calendar=cf_units.CALENDAR_STANDARD)
            >>> u.title(10)
            '1970-01-01 10:00:00'

        """
        if self.is_time_reference():
            dt = self.num2date(value)
            result = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            result = '%s %s' % (str(value), self)
        return result

    @property
    def modulus(self):
        """
        *(read-only)* Return the modulus value of the unit.

        Convenience method that returns the unit modulus value as follows,
            * 'radians' - pi*2
            * 'degrees' - 360.0
            * Otherwise None.

        Returns:
            float.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('degrees')
            >>> u.modulus
            360.0

        """

        if self == 'radians':
            result = np.pi * 2
        elif self == 'degrees':
            result = 360.0
        else:
            result = None
        return result

    def is_convertible(self, other):
        """
        Return whether two units are convertible.

        Args:

        * other (Unit): Unit to be compared.

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> v = cf_units.Unit('kilometers')
            >>> u.is_convertible(v)
            True

        """
        other = as_unit(other)
        if self.is_unknown() or self.is_no_unit() or other.is_unknown() or \
           other.is_no_unit():
            result = False
        else:
            result = (self.calendar == other.calendar and
                      _ut_are_convertible(self.ut_unit, other.ut_unit) != 0)
        return result

    def is_dimensionless(self):
        """
        Return whether the unit is dimensionless.

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> u.is_dimensionless()
            False
            >>> u = cf_units.Unit('1')
            >>> u.is_dimensionless()
            True

        """
        return (self.category == _CATEGORY_UDUNIT and
                bool(_ut_is_dimensionless(self.ut_unit)))

    def is_unknown(self):
        """
        Return whether the unit is defined to be an *unknown* unit.

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('unknown')
            >>> u.is_unknown()
            True
            >>> u = cf_units.Unit('meters')
            >>> u.is_unknown()
            False

        """
        return self.category == _CATEGORY_UNKNOWN

    def is_no_unit(self):
        """
        Return whether the unit is defined to be a *no_unit* unit.

        Typically, a quantity such as a string, will have no associated
        unit to describe it. Such a class of quantity may be defined
        using the *no_unit* unit.

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('no unit')
            >>> u.is_no_unit()
            True
            >>> u = cf_units.Unit('meters')
            >>> u.is_no_unit()
            False

        """
        return self.category == _CATEGORY_NO_UNIT

    def format(self, option=None):
        """
        Return a formatted string representation of the binary unit.

        Args:

        * option (cf_units.UT_FORMATS):
            Set the encoding option of the formatted string representation.
            Valid encoding options may be one of the following enumerations:

            * Unit.UT_ASCII
            * Unit.UT_ISO_8859_1
            * Unit.UT_LATIN1
            * Unit.UT_UTF8
            * Unit.UT_NAMES
            * Unit.UT_DEFINITION

            Multiple options may be combined within a list. The default
            option is cf_units.UT_ASCII.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> u.format()
            'm'
            >>> u.format(cf_units.UT_NAMES)
            'meter'
            >>> u.format(cf_units.UT_DEFINITION)
            'm'

        """
        if self.is_unknown():
            return _UNKNOWN_UNIT_STRING
        elif self.is_no_unit():
            return _NO_UNIT_STRING
        else:
            bitmask = UT_ASCII
            if option is not None:
                if not isinstance(option, list):
                    option = [option]
                for i in option:
                    bitmask |= i
            string_buffer = ctypes.create_string_buffer(_STRING_BUFFER_DEPTH)
            depth = _ut_format(self.ut_unit, string_buffer,
                               ctypes.sizeof(string_buffer), bitmask)
            if depth < 0:
                self._raise_error('Failed to format %r' % self)
        return str(string_buffer.value.decode('ascii'))

    @property
    def name(self):
        """
        *(read-only)* The full name of the unit.

        Formats the binary unit into a string representation using
        method :func:`cf_units.Unit.format` with keyword argument
        option=cf_units.UT_NAMES.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('watts')
            >>> u.name
            'watt'

        """
        return self.format(UT_NAMES)

    @property
    def symbol(self):
        """
        *(read-only)* The symbolic representation of the unit.

        Formats the binary unit into a string representation using
        method :func:`cf_units.Unit.format`.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('watts')
            >>> u.symbol
            'W'

        """
        if self.is_unknown():
            result = _UNKNOWN_UNIT_SYMBOL
        elif self.is_no_unit():
            result = _NO_UNIT_SYMBOL
        else:
            result = self.format()
        return result

    @property
    def definition(self):
        """
        *(read-only)* The symbolic decomposition of the unit.

        Formats the binary unit into a string representation using
        method :func:`cf_units.Unit.format` with keyword argument
        option=cf_units.UT_DEFINITION.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('watts')
            >>> u.definition
            'm2.kg.s-3'

        """
        if self.is_unknown():
            result = _UNKNOWN_UNIT_SYMBOL
        elif self.is_no_unit():
            result = _NO_UNIT_SYMBOL
        else:
            result = self.format(UT_DEFINITION)
        return result

    def offset_by_time(self, origin):
        """
        Returns the time unit offset with respect to the time origin.

        Args:

        * origin (float): Time origin as returned by the
          :func:`cf_units.encode_time` method.

        Returns:
            None.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('hours')
            >>> u.offset_by_time(cf_units.encode_time(1970, 1, 1, 0, 0, 0))
            Unit('hour since 1970-01-01 00:00:00.0000000 UTC')

        """

        if not isinstance(origin, (float, six.integer_types)):
            raise TypeError('a numeric type for the origin argument is'
                            ' required')
        ut_unit = _ut_offset_by_time(self.ut_unit, ctypes.c_double(origin))
        if not ut_unit:
            self._raise_error('Failed to offset %r' % self)
        calendar = None
        return _Unit(_CATEGORY_UDUNIT, ut_unit, calendar)

    def invert(self):
        """
        Invert the unit i.e. find the reciprocal of the unit, and return
        the Unit result.

        Returns:
            Unit.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> u.invert()
            Unit('meter^-1')

        """
        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot invert a 'no-unit'.")
        else:
            ut_unit = _ut_invert(self.ut_unit)
            if not ut_unit:
                self._raise_error('Failed to invert %r' % self)
            calendar = None
            result = _Unit(_CATEGORY_UDUNIT, ut_unit, calendar)
        return result

    def root(self, root):
        """
        Returns the given root of the unit.

        Args:

        * root (int): Value by which the unit root is taken.

        Returns:
            None.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters^2')
            >>> u.root(2)
            Unit('meter')

        .. note::

            Taking a fractional root of a unit is not supported.

        """
        try:
            root = ctypes.c_int(root)
        except TypeError:
            raise TypeError('An int type for the root argument'
                            ' is required')

        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot take the logarithm of a 'no-unit'.")
        else:
            # only update the unit if it is not scalar
            if self == Unit('1'):
                result = self
            else:
                ut_unit = _ut_root(self.ut_unit, root)
                if not ut_unit:
                    self._raise_error('Failed to take the root of %r' % self)
                calendar = None
                result = _Unit(_CATEGORY_UDUNIT, ut_unit, calendar)
        return result

    def log(self, base):
        """
        Returns the logorithmic unit corresponding to the given
        logorithmic base.

        Args:

        * base (int/float): Value of the logorithmic base.

        Returns:
            None.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> u.log(2)
            Unit('lb(re 1 meter)')

        """
        try:
            base = ctypes.c_double(base)
        except TypeError:
            raise TypeError('A numeric type for the base argument is required')

        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot take the logarithm of a 'no-unit'.")
        else:
            ut_unit = _ut_log(base, self.ut_unit)
            if not ut_unit:
                msg = 'Failed to calculate logorithmic base of %r' % self
                self._raise_error(msg)
            calendar = None
            result = _Unit(_CATEGORY_UDUNIT, ut_unit, calendar)
        return result

    def __str__(self):
        """
        Returns a simple string representation of the unit.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> str(u)
            'meters'

        """
        return self.origin or self.name

    def __repr__(self):
        """
        Returns a string representation of the unit object.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> repr(u)
            "Unit('meters')"

        """

        if self.calendar is None:
            result = "%s('%s')" % (self.__class__.__name__, self)
        else:
            result = "%s('%s', calendar='%s')" % (self.__class__.__name__,
                                                  self, self.calendar)
        return result

    def _offset_common(self, offset):
        try:
            offset = ctypes.c_double(offset)
        except TypeError:
            result = NotImplemented
        else:
            if self.is_unknown():
                result = self
            elif self.is_no_unit():
                raise ValueError("Cannot offset a 'no-unit'.")
            else:
                ut_unit = _ut_offset(self.ut_unit, offset)
                if not ut_unit:
                    self._raise_error('Failed to offset %r' % self)
                calendar = None
                result = _Unit(_CATEGORY_UDUNIT, ut_unit, calendar)
        return result

    def __add__(self, other):
        return self._offset_common(other)

    def __sub__(self, other):
        try:
            other = -other
        except TypeError:
            result = NotImplemented
        else:
            result = self._offset_common(-other)
        return result

    def _op_common(self, other, op_func):
        # Convienience method to create a new unit from an operation between
        # the units 'self' and 'other'.

        op_label = op_func.__name__.split('_')[1]

        other = as_unit(other)

        if self.is_no_unit() or other.is_no_unit():
            raise ValueError("Cannot %s a 'no-unit'." % op_label)

        if self.is_unknown() or other.is_unknown():
            result = _Unit(_CATEGORY_UNKNOWN, None)
        else:
            ut_unit = op_func(self.ut_unit, other.ut_unit)
            if not ut_unit:
                msg = 'Failed to %s %r by %r' % (op_label, self, other)
                self._raise_error(msg)
            calendar = None
            result = _Unit(_CATEGORY_UDUNIT, ut_unit, calendar)
        return result

    def __rmul__(self, other):
        # NB. Because we've subclassed a tuple, we need to define this to
        # prevent the default tuple-repetition behaviour.
        # ie. 2 * ('a', 'b') -> ('a', 'b', 'a', 'b')
        return self * other

    def __mul__(self, other):
        """
        Multiply the self unit by the other scale factor or unit and
        return the Unit result.

        Note that, multiplication involving an 'unknown' unit will always
        result in an 'unknown' unit.

        Args:

        * other (int/float/string/Unit): Multiplication scale
          factor or unit.

        Returns:
            Unit.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> v = cf_units.Unit('hertz')
            >>> u*v
            Unit('meter-second^-1')

        """
        return self._op_common(other, _ut_multiply)

    def __div__(self, other):
        """
        Divide the self unit by the other scale factor or unit and
        return the Unit result.

        Note that, division involving an 'unknown' unit will always
        result in an 'unknown' unit.

        Args:

        * other (int/float/string/Unit): Division scale factor or unit.

        Returns:
            Unit.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('m.s-1')
            >>> v = cf_units.Unit('hertz')
            >>> u/v
            Unit('meter')

        """
        return self._op_common(other, _ut_divide)

    def __truediv__(self, other):
        """
        Divide the self unit by the other scale factor or unit and
        return the Unit result.

        Note that, division involving an 'unknown' unit will always
        result in an 'unknown' unit.

        Args:

        * other (int/float/string/Unit): Division scale factor or unit.

        Returns:
            Unit.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('m.s-1')
            >>> v = cf_units.Unit('hertz')
            >>> u/v
            Unit('meter')

        """
        return self.__div__(other)

    def __pow__(self, power):
        """
        Raise the unit by the given power and return the Unit result.

        Note that, UDUNITS-2 does not support raising a
        non-dimensionless unit by a fractional power.
        Approximate floating point power behaviour has been implemented
        specifically for cf_units.

        Args:

        * power (int/float): Value by which the unit power is raised.

        Returns:
            Unit.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('meters')
            >>> u**2
            Unit('meter^2')

        """
        try:
            power = float(power)
        except ValueError:
            raise TypeError('A numeric value is required for the power'
                            ' argument.')

        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot raise the power of a 'no-unit'.")
        elif self == Unit('1'):
            # 1 ** N -> 1
            result = self
        else:
            # UDUNITS-2 does not support floating point raise/root.
            # But if the power is of the form 1/N, where N is an integer
            # (within a certain acceptable accuracy) then we can find the Nth
            # root.
            if not approx_equal(power, 0.0) and abs(power) < 1:
                if not approx_equal(1 / power, round(1 / power)):
                    raise ValueError('Cannot raise a unit by a decimal.')
                root = int(round(1 / power))
                result = self.root(root)
            else:
                # Failing that, check for powers which are (very nearly) simple
                # integer values.
                if not approx_equal(power, round(power)):
                    msg = 'Cannot raise a unit by a decimal (got %s).' % power
                    raise ValueError(msg)
                power = int(round(power))

                ut_unit = _ut_raise(self.ut_unit, ctypes.c_int(power))
                if not ut_unit:
                    self._raise_error('Failed to raise the power of %r' % self)
                result = _Unit(_CATEGORY_UDUNIT, ut_unit)
        return result

    def _identity(self):
        # Redefine the comparison/hash/ordering identity as used by
        # _OrderedHashable.
        return (self.name, self.calendar)

    def __eq__(self, other):
        """
        Compare the two units for equality and return the boolean result.

        Args:

        * other (string/Unit): Unit to be compared.

        Returns:
            Boolean.

        For example:

            >>> from cf_units import Unit
            >>> Unit('meters') == Unit('millimeters')
            False
            >>> Unit('meters') == 'm'
            True

        """
        other = as_unit(other)

        # Compare category (i.e. unknown, no_unit, etc.).
        if self.category != other.category:
            return False

        # Compare calendar as UDUNITS cannot handle calendars.
        if self.calendar != other.calendar:
            return False

        # Compare UDUNITS.
        res = _ut_compare(self.ut_unit, other.ut_unit)
        return res == 0

    def __ne__(self, other):
        """
        Compare the two units for inequality and return the boolean result.

        Args:

        * other (string/Unit): Unit to be compared.

        Returns:
            Boolean.

        For example:

            >>> from cf_units import Unit
            >>> Unit('meters') != Unit('millimeters')
            True
            >>> Unit('meters') != 'm'
            False

        """
        return not self == other

    def convert(self, value, other, ctype=FLOAT64, inplace=False):
        """
        Converts a single value or NumPy array of values from the current unit
        to the other target unit.

        If the units are not convertible, then no conversion will take place.

        Args:

        * value (int/float/numpy.ndarray):
            Value/s to be converted.
        * other (string/Unit):
            Target unit to convert to.
        * ctype (ctypes.c_float/ctypes.c_double):
            Floating point 32-bit single-precision (cf_units.FLOAT32) or
            64-bit double-precision (cf_units.FLOAT64) used for conversion
            when `value` is not a NumPy array or is a NumPy array composed of
            NumPy integers. The default is 64-bit double-precision conversion.
        * inplace (bool):
            If ``False``, return a deep copy of the value array. If ``True``,
            convert the values in-place. A new array will be created if
            ``value`` is an integer NumPy array.

        Returns:
            float or numpy.ndarray of appropriate float type.

        For example:

            >>> import cf_units
            >>> import numpy as np
            >>> c = cf_units.Unit('deg_c')
            >>> f = cf_units.Unit('deg_f')
            >>> c.convert(0, f)
            31.999999999999886
            >>> c.convert(0, f, cf_units.FLOAT32)
            32.0
            >>> a64 = np.arange(3, dtype=np.float64)
            >>> c.convert(a64, f)
            array([ 32. ,  33.8,  35.6])
            >>> a32 = np.arange(3, dtype=np.float32)
            >>> c.convert(a32, f)
            array([ 32.        ,  33.79999924,  35.59999847], dtype=float32)

        .. note::

           Conversion between unit calendars is not permitted.

        """
        other = as_unit(other)

        if self == other:
            return value

        if inplace:
            result = value
        else:
            result = copy.deepcopy(value)

        if self.is_convertible(other):
            # Use utime for converting reference times that are not using a
            # gregorian calendar as it handles these and udunits does not.
            if self.is_time_reference() \
                    and self.calendar != CALENDAR_GREGORIAN:
                ut1 = self.utime()
                ut2 = other.utime()
                result = ut2.date2num(ut1.num2date(result))
                # Preserve the datatype of the input array if it was float32.
                if (isinstance(value, np.ndarray) and
                   value.dtype == np.float32):
                    result = result.astype(np.float32)
            else:
                ut_converter = _ut_get_converter(self.ut_unit, other.ut_unit)
                if ut_converter:
                    if isinstance(result, np.ndarray):
                        # Can only handle array of np.float32 or np.float64 so
                        # cast array of ints to array of floats of requested
                        # precision.
                        if issubclass(result.dtype.type, np.integer):
                            result = result.astype(
                                _ctypes2numpy[ctype])
                        # Convert arrays with explicit endianness to native
                        # endianness: udunits seems to be tripped up by arrays
                        # with endianness other than native.
                        if result.dtype.byteorder != '=':
                            result = result.astype(
                                result.dtype.type)
                        # Strict type check of numpy array.
                        if result.dtype.type not in _numpy2ctypes:
                            raise TypeError(
                                "Expect a numpy array of '%s' or '%s'" %
                                tuple(sorted(_numpy2ctypes.keys())))
                        ctype = _numpy2ctypes[result.dtype.type]
                        pointer = result.ctypes.data_as(
                            ctypes.POINTER(ctype))
                        # Utilise global convenience dictionary
                        # _cv_convert_array
                        _cv_convert_array[ctype](ut_converter, pointer,
                                                 result.size, pointer)
                    else:
                        if ctype not in _cv_convert_scalar:
                            raise ValueError('Invalid target type. Can only '
                                             'convert to float or double.')
                        # Utilise global convenience dictionary
                        # _cv_convert_scalar
                        result = _cv_convert_scalar[ctype](ut_converter,
                                                           ctype(result))
                    _cv_free(ut_converter)
                else:
                    self._raise_error('Failed to convert %r to %r' %
                                      (self, other))
        else:
            raise ValueError("Unable to convert from '%r' to '%r'." %
                             (self, other))
        return result

    def utime(self):
        """
        Returns a netcdftime.utime object which performs conversions of
        numeric time values to/from datetime objects given the current
        calendar and unit time reference.

        The current unit time reference must be of the form:
        '<time-unit> since <time-origin>'
        i.e. 'hours since 1970-01-01 00:00:00'

        Returns:
            netcdftime.utime.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('hours since 1970-01-01 00:00:00',
            ...                   calendar=cf_units.CALENDAR_STANDARD)
            >>> ut = u.utime()
            >>> ut.num2date(2)
            datetime.datetime(1970, 1, 1, 2, 0)

        """

        #
        # ensure to strip out non-parsable 'UTC' postfix which
        # is generated by UDUNITS-2 formatted output
        #
        if self.calendar is None:
            raise ValueError('Unit has undefined calendar')
        return netcdftime.utime(str(self).rstrip(" UTC"), self.calendar)

    def date2num(self, date):
        """
        Returns the numeric time value calculated from the datetime
        object using the current calendar and unit time reference.

        The current unit time reference must be of the form:
        '<time-unit> since <time-origin>'
        i.e. 'hours since 1970-01-01 00:00:00'

        Works for scalars, sequences and numpy arrays. Returns a scalar
        if input is a scalar, else returns a numpy array.

        Args:

        * date (datetime):
            A datetime object or a sequence of datetime objects.
            The datetime objects should not include a time-zone offset.

        Returns:
            float or numpy.ndarray of float.

        For example:

            >>> import cf_units
            >>> import datetime
            >>> u = cf_units.Unit('hours since 1970-01-01 00:00:00',
            ...                   calendar=cf_units.CALENDAR_STANDARD)
            >>> u.date2num(datetime.datetime(1970, 1, 1, 5))
            5.00000000372529
            >>> u.date2num([datetime.datetime(1970, 1, 1, 5),
            ...             datetime.datetime(1970, 1, 1, 6)])
            array([ 5.,  6.])

        """

        cdf_utime = self.utime()
        date = _discard_microsecond(date)
        return cdf_utime.date2num(date)

    def num2date(self, time_value):
        """
        Returns a datetime-like object calculated from the numeric time
        value using the current calendar and the unit time reference.

        The current unit time reference must be of the form:
        '<time-unit> since <time-origin>'
        i.e. 'hours since 1970-01-01 00:00:00'

        The datetime objects returned are 'real' Python datetime objects
        if the date falls in the Gregorian calendar (i.e. the calendar
        is 'standard', 'gregorian', or 'proleptic_gregorian' and the
        date is after 1582-10-15). Otherwise a 'phoney' datetime-like
        object (netcdftime.datetime) is returned which can handle dates
        that don't exist in the Proleptic Gregorian calendar.

        Works for scalars, sequences and numpy arrays. Returns a scalar
        if input is a scalar, else returns a numpy array.

        Args:

        * time_value (float): Numeric time value/s. Maximum resolution
          is 1 second.

        Returns:
            datetime, or numpy.ndarray of datetime object.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('hours since 1970-01-01 00:00:00',
            ...                   calendar=cf_units.CALENDAR_STANDARD)
            >>> u.num2date(6)
            datetime.datetime(1970, 1, 1, 6, 0)
            >>> u.num2date([6, 7])
            array([datetime.datetime(1970, 1, 1, 6, 0),
                   datetime.datetime(1970, 1, 1, 7, 0)], dtype=object)

        """
        cdf_utime = self.utime()
        return _num2date_to_nearest_second(time_value, cdf_utime)
