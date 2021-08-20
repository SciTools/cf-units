# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
Units of measure.

Provision of a wrapper class to support Unidata/UCAR UDUNITS-2, and the
cftime calendar functionality.

See also: `UDUNITS-2
<http://www.unidata.ucar.edu/software/udunits>`_.

"""

import copy
from contextlib import contextmanager

import cftime
import numpy as np

from cf_units import _udunits2 as _ud
from cf_units._udunits2 import (
    UT_ASCII,
    UT_DEFINITION,
    UT_ISO_8859_1,
    UT_LATIN1,
    UT_NAMES,
    UT_UTF8,
)

from . import config
from ._version import version as __version__  # noqa: F401
from .util import _OrderedHashable, approx_equal

__all__ = [
    "CALENDAR_STANDARD",
    "CALENDAR_GREGORIAN",
    "CALENDAR_PROLEPTIC_GREGORIAN",
    "CALENDAR_NO_LEAP",
    "CALENDAR_JULIAN",
    "CALENDAR_ALL_LEAP",
    "CALENDAR_365_DAY",
    "CALENDAR_366_DAY",
    "CALENDAR_360_DAY",
    "CALENDARS",
    "CALENDAR_ALIASES",
    "UT_NAMES",
    "UT_DEFINITION",
    "UT_ASCII",
    "FLOAT32",
    "FLOAT64",
    "is_time",
    "is_vertical",
    "Unit",
    "date2num",
    "decode_time",
    "encode_clock",
    "encode_date",
    "encode_time",
    "num2date",
    "num2pydate",
    "suppress_errors",
]


########################################################################
#
# module level constants
#
########################################################################

#
# default constants
#
EPOCH = "1970-01-01 00:00:00"
_UNKNOWN_UNIT_STRING = "unknown"
_UNKNOWN_UNIT_SYMBOL = "?"
_UNKNOWN_UNIT = [_UNKNOWN_UNIT_STRING, _UNKNOWN_UNIT_SYMBOL, "???", ""]
_NO_UNIT_STRING = "no_unit"
_NO_UNIT_SYMBOL = "-"
_NO_UNIT = [_NO_UNIT_STRING, _NO_UNIT_SYMBOL, "no unit", "no-unit", "nounit"]
_UNIT_DIMENSIONLESS = "1"
_OP_SINCE = " since "
_CATEGORY_UNKNOWN, _CATEGORY_NO_UNIT, _CATEGORY_UDUNIT = range(3)


#
# libudunits2 constants
#
UT_FORMATS = [
    UT_ASCII,
    UT_ISO_8859_1,
    UT_LATIN1,
    UT_UTF8,
    UT_NAMES,
    UT_DEFINITION,
]

#
# cftime constants
#
CALENDAR_STANDARD = "standard"
CALENDAR_GREGORIAN = "gregorian"
CALENDAR_PROLEPTIC_GREGORIAN = "proleptic_gregorian"
CALENDAR_NO_LEAP = "noleap"
CALENDAR_JULIAN = "julian"
CALENDAR_ALL_LEAP = "all_leap"
CALENDAR_365_DAY = "365_day"
CALENDAR_366_DAY = "366_day"
CALENDAR_360_DAY = "360_day"

#: The calendars recognised by cf_units.
#: These are accessible as strings, or as constants in the form
#: ``cf_units.CALENDAR_{ calendar_name.upper() }``. For example,
#: ``cf_units.CALENDAR_NO_LEAP`` and ``cf_units.CALENDAR_366_DAY``.
CALENDARS = [
    CALENDAR_STANDARD,
    CALENDAR_GREGORIAN,
    CALENDAR_PROLEPTIC_GREGORIAN,
    CALENDAR_NO_LEAP,
    CALENDAR_JULIAN,
    CALENDAR_ALL_LEAP,
    CALENDAR_365_DAY,
    CALENDAR_366_DAY,
    CALENDAR_360_DAY,
]

#: Where calendars have multiple names, we map the alias to the
#: definitive form.
CALENDAR_ALIASES = {
    CALENDAR_STANDARD: CALENDAR_GREGORIAN,
    CALENDAR_NO_LEAP: CALENDAR_365_DAY,
    CALENDAR_ALL_LEAP: CALENDAR_366_DAY,
}


#
# floating point types
#
FLOAT32 = np.float32
FLOAT64 = np.float64

########################################################################
#
# module level statements
#
########################################################################

# Convenience dictionary for the Unit convert method.
_cv_convert_scalar = {FLOAT32: _ud.convert_float, FLOAT64: _ud.convert_double}
_cv_convert_array = {FLOAT32: _ud.convert_floats, FLOAT64: _ud.convert_doubles}

# Map of ut_encodings to encoding strings
_encoding_lookup = {
    UT_ASCII: "ascii",
    UT_ISO_8859_1: "iso_8859_1",
    UT_LATIN1: "latin1",
    UT_UTF8: "utf-8",
}


@contextmanager
def suppress_errors():
    """
    Suppresses all error messages from UDUNITS-2.

    """
    _default_handler = _ud.set_error_message_handler(_ud.ignore)
    try:
        yield
    finally:
        _ud.set_error_message_handler(_default_handler)


#
# load the UDUNITS-2 xml-formatted unit-database
#:
# Ignore standard noisy UDUNITS-2 start-up.
with suppress_errors():
    # Load the unit-database from the default location (modified via
    # the UDUNITS2_XML_PATH environment variable) and if that fails look
    # relative to sys.prefix to support environments such as conda.
    try:
        _ud_system = _ud.read_xml()
    except _ud.UdunitsError:
        try:
            _ud_system = _ud.read_xml(config.get_xml_path())
        except _ud.UdunitsError as e:
            error_msg = ': "%s"' % e.error_msg() if e.errnum else ""
            raise OSError(
                "[%s] Failed to open UDUNITS-2 XML unit database%s"
                % (e.status_msg(), error_msg)
            )


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

    return _ud.encode_time(year, month, day, hour, minute, second)


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

    return _ud.encode_date(year, month, day)


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

    return _ud.encode_clock(hour, minute, second)


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
    return _ud.decode_time(time)


def date2num(date, unit, calendar):
    """
    Return numeric time value (resolution of 1 second) encoding of
    datetime object.

    The units of the numeric time values are described by the unit and
    calendar arguments. The datetime objects must be in UTC with no
    time-zone offset. If there is a time-zone offset in unit, it will be
    applied to the returned numeric values.

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
        >>> dt1 = datetime.datetime(1970, 1, 1, 6, 30, 0)
        >>> dt2 = datetime.datetime(1970, 1, 1, 7, 30, 0)
        >>> cf_units.date2num(dt1, 'hours since 1970-01-01 00:00:00',
        ...               cf_units.CALENDAR_STANDARD)
        6.5
        >>> cf_units.date2num([dt1, dt2], 'hours since 1970-01-01 00:00:00',
        ...               cf_units.CALENDAR_STANDARD)
        array([6.5, 7.5])

    """

    #
    # ensure to strip out any 'UTC' postfix which is generated by
    # UDUNITS-2 formatted output and causes the cftime parser
    # to choke
    #
    unit_string = unit.rstrip(" UTC")
    if unit_string.endswith(" since epoch"):
        unit_string = unit_string.replace("epoch", EPOCH)
    unit_inst = Unit(unit_string, calendar=calendar)
    return unit_inst.date2num(date)


def _discard_microsecond(date):
    """
    Return a date with the microsecond component discarded.

    Works for scalars, sequences and numpy arrays. Returns a scalar
    if input is a scalar, else returns a numpy array.

    Args:

    * date (datetime.datetime or cftime.datetime):
        Date value/s

    Returns:
        datetime, or numpy.ndarray of datetime object.

    """
    dates = np.asanyarray(date)
    shape = dates.shape
    dates = dates.ravel()

    # using the "and" pattern to support masked arrays of datetimes
    dates = np.array([dt and dt.replace(microsecond=0) for dt in dates])
    result = dates[0] if shape == () else dates.reshape(shape)

    return result


def num2date(
    time_value,
    unit,
    calendar,
    only_use_cftime_datetimes=True,
    only_use_python_datetimes=False,
):
    """
    Return datetime encoding of numeric time value (resolution of 1 second).

    The units of the numeric time value are described by the unit and
    calendar arguments. The returned datetime object represent UTC with
    no time-zone offset, even if the specified unit contain a time-zone
    offset.

    By default, the datetime instances returned are cftime.datetime objects,
    regardless of calendar.  If the only_use_cftime_datetimes keyword is set to
    False, they are datetime.datetime objects if the date falls in the
    Gregorian calendar (i.e. calendar is 'proleptic_gregorian', 'standard' or
    'gregorian' and the date is after 1582-10-15). The datetime instances
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

    Kwargs:

    * only_use_cftime_datetimes (bool):
        If True, will always return cftime datetime objects, regardless of
        calendar.  If False, returns datetime.datetime instances where
        possible.  Defaults to True.

    * only_use_python_datetimes (bool):
        If True, will always return datetime.datetime instances where
        possible, and raise an exception if not.  Ignored if
        only_use_cftime_datetimes is True.  Defaults to False.

    Returns:
        datetime, or numpy.ndarray of datetime object.

    For example:

        >>> import cf_units
        >>> import datetime
        >>> print(cf_units.num2date(6, 'hours since 1970-01-01 00:00:00',
        ...                         cf_units.CALENDAR_STANDARD))
        1970-01-01 06:00:00
        >>> dts = cf_units.num2date([6, 7], 'hours since 1970-01-01 00:00:00',
        ...                         cf_units.CALENDAR_STANDARD)
        >>> [str(dt) for dt in dts]
        ['1970-01-01 06:00:00', '1970-01-01 07:00:00']

    """

    #
    # ensure to strip out any 'UTC' postfix which is generated by
    # UDUNITS-2 formatted output and causes the cftime parser
    # to choke
    #
    unit_string = unit.rstrip(" UTC")
    if unit_string.endswith(" since epoch"):
        unit_string = unit_string.replace("epoch", EPOCH)
    unit_inst = Unit(unit_string, calendar=calendar)
    return unit_inst.num2date(
        time_value,
        only_use_cftime_datetimes=only_use_cftime_datetimes,
        only_use_python_datetimes=only_use_python_datetimes,
    )


def num2pydate(time_value, unit, calendar):
    """
    Convert time value(s) to python datetime.datetime objects, or raise an
    exception if this is not possible.  Same as::

        num2date(time_value, unit, calendar,
                 only_use_cftime_datetimes=False,
                 only_use_python_datetimes=True)

    """
    return num2date(
        time_value,
        unit,
        calendar,
        only_use_cftime_datetimes=False,
        only_use_python_datetimes=True,
    )


def _num2date_to_nearest_second(
    time_value,
    unit,
    only_use_cftime_datetimes=True,
    only_use_python_datetimes=False,
):
    """
    Return datetime encoding of numeric time value with respect to the given
    time reference units, with a resolution of 1 second.

    * time_value (float):
        Numeric time value/s.
    * unit (Unit):
        cf_units.Unit object with which to perform the conversion/s.

    * only_use_cftime_datetimes (bool):
        If True, will always return cftime datetime objects, regardless of
        calendar.  If False, returns datetime.datetime instances where
        possible.  Defaults to True.

    * only_use_python_datetimes (bool):
        If True, will always return datetime.datetime instances where
        possible, and raise an exception if not.  Ignored if
        only_use_cftime_datetimes is True.  Defaults to False.

    Returns:
        datetime, or numpy.ndarray of datetime object.

    """
    time_values = np.asanyarray(time_value)
    shape = time_values.shape
    time_values = time_values.ravel()

    # We account for the edge case where the time is in seconds and has a
    # half second: cftime.num2date() may produce a date that would round
    # down.
    #
    # Note that this behaviour is different to the num2date function in version
    # 1.1 and earlier of cftime that didn't have microsecond precision. In
    # those versions, a half-second value would be rounded up or down
    # arbitrarily. It is probably not possible to replicate that behaviour with
    # later versions, if one wished to do so for the sake of consistency.
    cftime_unit = unit.cftime_unit
    time_units = cftime_unit.split(" ")[0]
    has_half_seconds = np.logical_and(
        time_units == "seconds", time_values % 1.0 == 0.5
    )
    num2date_kwargs = dict(
        units=cftime_unit,
        calendar=unit.calendar,
        only_use_cftime_datetimes=only_use_cftime_datetimes,
        only_use_python_datetimes=only_use_python_datetimes,
    )
    dates = cftime.num2date(time_values, **num2date_kwargs)
    try:
        # We can assume all or none of the dates have a microsecond attribute
        microseconds = np.array([d.microsecond if d else 0 for d in dates])
    except AttributeError:
        microseconds = 0
    round_mask = np.logical_or(has_half_seconds, microseconds != 0)
    ceil_mask = np.logical_or(has_half_seconds, microseconds >= 500000)
    if time_values[ceil_mask].size > 0:
        useconds = Unit("second")
        second_frac = useconds.convert(0.75, time_units)
        dates[ceil_mask] = cftime.num2date(
            time_values[ceil_mask] + second_frac, **num2date_kwargs
        )
    dates[round_mask] = _discard_microsecond(dates[round_mask])
    result = dates[0] if shape == () else dates.reshape(shape)
    return result


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
        use_cache = isinstance(unit, (str,)) or unit is None
        if use_cache:
            result = _CACHE.get(unit)
        if result is None:
            # Typically unit is a string, however we cater for other types of
            # 'unit' (e.g. iris.unit.Unit).
            result = Unit(unit, calendar=getattr(unit, "calendar", None))
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


def _ud_value_error(ud_err, message):
    """
    Return a ValueError that has extra context from a _udunits2.UdunitsError.

    """
    # NOTE: We aren't raising here, just giving the caller a well formatted
    # exception that they can raise themselves.

    ud_msg = ud_err.error_msg()
    if ud_msg:
        message = "{}: {}".format(message, ud_msg)

    message = "[{status}] {message}".format(
        status=ud_err.status_msg(), message=message
    )

    return ValueError(message)


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
        # Implements the required interface for an _OrderedHashable.
        # This will also ensure a Unit._init(*Unit.names) method exists.
        for name, value in zip(self._names, values):
            object.__setattr__(self, name, value)

    # Provide hash semantics

    def _identity(self):
        return (self.name, self.calendar)

    def __hash__(self):
        return hash(self._identity())

    # Provide default ordering semantics

    def __lt__(self, other):
        return self._identity() < other._identity()

    # Prevent attribute updates

    def __setattr__(self, name, value):
        raise AttributeError(
            "Instances of %s are immutable" % type(self).__name__
        )

    def __delattr__(self, name):
        raise AttributeError(
            "Instances of %s are immutable" % type(self).__name__
        )

    # Declare the attribute names relevant to the ordered and hashable
    #  behaviour.
    _names = ("category", "ut_unit", "calendar", "origin")

    category = None
    "Is this an unknown unit, a no-unit, or a UDUNITS-2 unit."

    ut_unit = None
    "Reference to the quantity defining the UDUNITS-2 unit."

    calendar = None
    "Represents the unit calendar name, see cf_units.CALENDARS"

    origin = None
    "The original string used to create this unit."

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
        ut_unit = _ud.NULL_UNIT
        calendar_ = None

        encoding = UT_UTF8

        if unit is None:
            unit = ""

        unit = str(unit).strip()

        if unit.lower().endswith(" utc"):
            unit = unit[: unit.lower().rfind(" utc")]

        if unit.endswith(" since epoch"):
            unit = unit.replace("epoch", EPOCH)

        if "#" in unit:
            unit = unit.replace("#", "1")

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
            str_unit = unit
            try:
                ut_unit = _ud.parse(_ud_system, unit.encode("utf8"), encoding)
            except _ud.UdunitsError as exception:
                value_error = _ud_value_error(
                    exception, 'Failed to parse unit "{}"'.format(str_unit)
                )
                raise value_error from None
            if _OP_SINCE in unit.lower():
                if calendar is None:
                    calendar_ = CALENDAR_GREGORIAN
                elif isinstance(calendar, (str,)):
                    calendar_ = calendar.lower()
                    if calendar_ in CALENDAR_ALIASES:
                        calendar_ = CALENDAR_ALIASES[calendar_]
                    if calendar_ not in CALENDARS:
                        msg = "{!r} is an unsupported calendar."
                        raise ValueError(msg.format(calendar))
                else:
                    msg = "Expected string-like calendar argument, got {!r}."
                    raise TypeError(msg.format(type(calendar)))

        # Call the OrderedHashable's init.
        self._init(
            category,
            ut_unit,
            calendar_,
            unit,
        )

    @classmethod
    def _new_from_existing_ut(
        cls, category, ut_unit, calendar=None, origin=None
    ):
        # Short-circuit __init__ if we know what we are doing and already
        # have a UT handle.
        unit = cls.__new__(cls)
        unit._init(category, ut_unit, calendar, origin)
        return unit

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
        return {"unit_text": self.origin, "calendar": self.calendar}

    def __setstate__(self, state):
        # object reconstruction method for Pickle.load()
        # intercept the Pickle.load() operation and call own __init__ again
        #  - this is to ensure a valid ut_unit attribute (as these
        #    handles aren't persistent)
        self.__init__(state["unit_text"], calendar=state["calendar"])

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
            day = _ud.get_unit_by_name(_ud_system, b"day")
            result = _ud.are_convertible(self.ut_unit, day)
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
            bar = _ud.get_unit_by_name(_ud_system, b"bar")
            result = _ud.are_convertible(self.ut_unit, bar)
            if not result:
                meter = _ud.get_unit_by_name(_ud_system, b"meter")
                result = _ud.are_convertible(self.ut_unit, meter)
        return result

    def is_udunits(self):
        """Return whether the unit is a vaild unit of UDUNITS."""
        return self.ut_unit is not _ud.NULL_UNIT

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

    def is_long_time_interval(self):
        """
        Defines whether this unit describes a time unit with a long time
        interval ("months" or "years"). These long time intervals *are*
        supported by `UDUNITS2` but are not supported by `cftime`. This
        discrepancy means we cannot run self.num2date() on a time unit with
        a long time interval.

        Returns:
            Boolean.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('days since epoch')
            >>> u.is_long_time_interval()
            False
            >>> u = cf_units.Unit('years since epoch')
            >>> u.is_long_time_interval()
            True

        """
        result = False
        long_time_intervals = ["year", "month"]
        if self.is_time_reference():
            result = any(
                interval in self.origin for interval in long_time_intervals
            )
        return result

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
            result = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            result = "%s %s" % (str(value), self)
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

        if self == "radians":
            result = np.pi * 2
        elif self == "degrees":
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
        if (
            self.is_unknown()
            or self.is_no_unit()
            or other.is_unknown()
            or other.is_no_unit()
        ):
            result = False
        else:
            result = self.calendar == other.calendar and _ud.are_convertible(
                self.ut_unit, other.ut_unit
            )
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
        return self.category == _CATEGORY_UDUNIT and bool(
            _ud.is_dimensionless(self.ut_unit)
        )

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
        return self.category == _CATEGORY_UNKNOWN or self.ut_unit is None

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
            Set the option of the formatted string representation.
            Valid encoding options may be at most one of the following
            enumerations:
            * Unit.UT_ASCII
            * Unit.UT_ISO_8859_1
            * Unit.UT_LATIN1
            * Unit.UT_UTF8

            Any combination of the following may also be used:
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
            encoding = bitmask & (
                UT_ASCII | UT_ISO_8859_1 | UT_LATIN1 | UT_UTF8
            )
            encoding_str = _encoding_lookup[encoding]
            result = _ud.format(self.ut_unit, bitmask)

            result = str(result.decode(encoding_str))
            return result

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
            Unit('h @ 19700101T000000.0000000 UTC')

        """

        if not isinstance(origin, (float, (int,))):
            raise TypeError(
                "a numeric type for the origin argument is" " required"
            )
        try:
            ut_unit = _ud.offset_by_time(self.ut_unit, origin)
        except _ud.UdunitsError as exception:
            value_error = _ud_value_error(
                exception, "Failed to offset {!r}".format(self)
            )
            raise value_error from None
        calendar = None
        return Unit._new_from_existing_ut(_CATEGORY_UDUNIT, ut_unit, calendar)

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
            Unit('m-1')

        """
        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot invert a 'no-unit'.")
        else:
            ut_unit = _ud.invert(self.ut_unit)
            result = Unit._new_from_existing_ut(
                _CATEGORY_UDUNIT, ut_unit, calendar=None
            )
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
            Unit('m')

        .. note::

            Taking a fractional root of a unit is not supported.

        """
        if round(root) != root:
            raise TypeError("An integer for the root argument is required")
        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot take the root of a 'no-unit'.")
        else:
            # only update the unit if it is not scalar
            if self == Unit("1"):
                result = self
            else:
                try:
                    ut_unit = _ud.root(self.ut_unit, root)
                except _ud.UdunitsError as exception:
                    value_error = _ud_value_error(
                        exception,
                        "Failed to take the root of {!r}".format(self),
                    )
                    raise value_error from None
                calendar = None
                result = Unit._new_from_existing_ut(
                    _CATEGORY_UDUNIT, ut_unit, calendar
                )
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
            Unit('lb(re 1 m)')

        """
        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot take the logarithm of a 'no-unit'.")
        else:
            try:
                ut_unit = _ud.log(base, self.ut_unit)
            except TypeError:
                raise TypeError(
                    "A numeric type for the base argument is " " required"
                )
            except _ud.UdunitsError as exception:
                value_err = _ud_value_error(
                    exception,
                    "Failed to calculate logorithmic base "
                    "of {!r}".format(self),
                )
                raise value_err from None
            calendar = None
            result = Unit._new_from_existing_ut(
                _CATEGORY_UDUNIT, ut_unit, calendar
            )
        return result

    def __str__(self):
        """
        Returns a simple string representation of the unit.

        Returns:
            string.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('miles/hour')
            >>> str(u)
            'miles/hour'

        """
        return self.origin or self.symbol

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
            result = "{}('{}')".format(self.__class__.__name__, self)
        else:
            result = "{}('{}', calendar='{}')".format(
                self.__class__.__name__, self, self.calendar
            )
        return result

    def _offset_common(self, offset):
        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot offset a 'no-unit'.")
        else:
            try:
                ut_unit = _ud.offset(self.ut_unit, offset)
            except TypeError:
                result = NotImplemented
            else:
                result = Unit._new_from_existing_ut(
                    _CATEGORY_UDUNIT, ut_unit, calendar=None
                )
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

        op_label = op_func.__name__

        other = as_unit(other)

        if self.is_no_unit() or other.is_no_unit():
            raise ValueError("Cannot %s a 'no-unit'." % op_label)

        if self.is_unknown() or other.is_unknown():
            result = Unit(_UNKNOWN_UNIT_STRING)
        else:
            try:
                ut_unit = op_func(self.ut_unit, other.ut_unit)
            except _ud.UdunitsError as exception:
                value_err = _ud_value_error(
                    exception,
                    "Failed to {} {!r} by {!r}".format(op_label, self, other),
                )
                raise value_err from None
            calendar = None
            result = Unit._new_from_existing_ut(
                _CATEGORY_UDUNIT, ut_unit, calendar
            )
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
            Unit('m.s-1')

        """
        return self._op_common(other, _ud.multiply)

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
            >>> u / v
            Unit('m')

        """
        return self._op_common(other, _ud.divide)

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
            >>> u / v
            Unit('m')

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
            Unit('m2')

        """
        try:
            power = float(power)
        except ValueError:
            raise TypeError(
                "A numeric value is required for the power" " argument."
            )

        if self.is_unknown():
            result = self
        elif self.is_no_unit():
            raise ValueError("Cannot raise the power of a 'no-unit'.")
        elif self == Unit("1"):
            # 1 ** N -> 1
            result = self
        else:
            # UDUNITS-2 does not support floating point raise/root.
            # But if the power is of the form 1/N, where N is an integer
            # (within a certain acceptable accuracy) then we can find the Nth
            # root.
            if not approx_equal(power, 0.0) and abs(power) < 1:
                if not approx_equal(1 / power, round(1 / power)):
                    raise ValueError("Cannot raise a unit by a decimal.")
                root = int(round(1 / power))
                result = self.root(root)
            else:
                # Failing that, check for powers which are (very nearly) simple
                # integer values.
                if not approx_equal(power, round(power)):
                    msg = "Cannot raise a unit by a decimal (got %s)." % power
                    raise ValueError(msg)
                power = int(round(power))

                try:
                    ut_unit = _ud.raise_(self.ut_unit, power)
                except _ud.UdunitsError as exception:
                    value_err = _ud_value_error(
                        exception,
                        "Failed to raise the power of {!r}".format(self),
                    )
                    raise value_err from None
                result = Unit._new_from_existing_ut(_CATEGORY_UDUNIT, ut_unit)
        return result

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
        try:
            other = as_unit(other)
        except ValueError:
            return NotImplemented

        # Compare category (i.e. unknown, no_unit, etc.).
        if self.category != other.category:
            return False

        # Compare calendar as UDUNITS cannot handle calendars.
        if self.calendar != other.calendar:
            return False

        # Compare UDUNITS.
        res = _ud.compare(self.ut_unit, other.ut_unit)
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
        * ctype (cf_units.FLOAT32/cf_units.FLOAT64):
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
            array([32. , 33.8, 35.6])
            >>> a32 = np.arange(3, dtype=np.float32)
            >>> c.convert(a32, f)
            array([32. , 33.8, 35.6], dtype=float32)

        .. note::

           Conversion between unit calendars is not permitted unless the
           calendars are aliases, see :attr:`cf_units.CALENDAR_ALIASES`.

           >>> from cf_units import Unit
           >>> a = Unit('days since 1850-1-1', calendar='gregorian')
           >>> b = Unit('days since 1851-1-1', calendar='standard')
           >>> a.convert(365.75, b)
           0.75

        """
        other = as_unit(other)

        if self == other:
            return value

        if self.is_convertible(other):
            if inplace:
                result = value
            else:
                result = copy.deepcopy(value)
            # Use cftime for converting reference times that are not using a
            # gregorian calendar as it handles these and udunits does not.
            if (
                self.is_time_reference()
                and self.calendar != CALENDAR_GREGORIAN
            ):
                result_datetimes = cftime.num2date(
                    result, self.cftime_unit, self.calendar
                )
                result = cftime.date2num(
                    result_datetimes, other.cftime_unit, other.calendar
                )
                convert_type = isinstance(
                    value, np.ndarray
                ) and np.issubsctype(value.dtype, np.floating)
                if convert_type:
                    result = result.astype(value.dtype)
            else:
                try:
                    ut_converter = _ud.get_converter(
                        self.ut_unit, other.ut_unit
                    )
                except _ud.UdunitsError as exception:
                    value_err = _ud_value_error(
                        exception,
                        "Failed to convert {!r} to {!r}".format(self, other),
                    )
                    raise value_err from None
                if isinstance(result, np.ndarray):
                    # Can only handle array of np.float32 or np.float64 so
                    # cast array of ints to array of floats of requested
                    # precision.
                    if issubclass(result.dtype.type, np.integer):
                        result = result.astype(ctype)
                    # Convert arrays with explicit endianness to native
                    # endianness: udunits seems to be tripped up by arrays
                    # with endianness other than native.
                    if result.dtype.byteorder != "=":
                        if inplace:
                            raise ValueError(
                                "Unable to convert non-native byte ordered "
                                "array in-place. Consider byte-swapping "
                                "first."
                            )
                        else:
                            result = result.astype(result.dtype.type)
                    # Strict type check of numpy array.
                    if result.dtype.type not in (np.float32, np.float64):
                        raise TypeError(
                            "Expect a numpy array of '%s' or '%s'"
                            % np.float32,
                            np.float64,
                        )
                    ctype = result.dtype.type
                    # Utilise global convenience dictionary
                    # _cv_convert_array to convert our array in 1d form
                    result_tmp = result.ravel(order="A")
                    # Do the actual conversion.
                    _cv_convert_array[ctype](
                        ut_converter, result_tmp, result_tmp
                    )
                    # If result_tmp was a copy, not a view (i.e. not C
                    # contiguous), copy the data back to the original.
                    if not np.shares_memory(result, result_tmp):
                        result_tmp = result_tmp.reshape(
                            result.shape, order="A"
                        )
                        if isinstance(result, np.ma.MaskedArray):
                            result.data[...] = result_tmp
                        else:
                            result[...] = result_tmp
                else:
                    if ctype not in _cv_convert_scalar:
                        raise ValueError(
                            "Invalid target type. Can only "
                            "convert to float or double."
                        )
                    # Utilise global convenience dictionary
                    # _cv_convert_scalar
                    result = _cv_convert_scalar[ctype](ut_converter, result)
            return result
        else:
            raise ValueError(
                "Unable to convert from '%r' to '%r'." % (self, other)
            )

    @property
    def cftime_unit(self):
        """
        Returns a string suitable for passing as a unit to cftime.num2date and
        cftime.date2num.

        """
        if self.calendar is None:
            raise ValueError("Unit has undefined calendar")

        # `cftime` cannot parse long time intervals ("months" or "years").
        if self.is_long_time_interval():
            interval = self.origin.split(" ")[0]
            emsg = (
                'Time units with interval of "months", "years" '
                '(or singular of these) cannot be processed, got "{!s}".'
            )
            raise ValueError(emsg.format(interval))

        #
        # ensure to strip out non-parsable 'UTC' postfix, which
        # is generated by UDUNITS-2 formatted output
        #
        return str(self).rstrip(" UTC")

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
            >>> u.date2num(datetime.datetime(1970, 1, 1, 5, 30))
            5.5
            >>> u.date2num([datetime.datetime(1970, 1, 1, 5, 30),
            ...             datetime.datetime(1970, 1, 1, 6, 30)])
            array([5.5, 6.5])

        """

        date = _discard_microsecond(date)
        return cftime.date2num(date, self.cftime_unit, self.calendar)

    def num2date(
        self,
        time_value,
        only_use_cftime_datetimes=True,
        only_use_python_datetimes=False,
    ):
        """
        Returns a datetime-like object calculated from the numeric time
        value using the current calendar and the unit time reference.

        The current unit time reference must be of the form:
        '<time-unit> since <time-origin>'
        i.e. 'hours since 1970-01-01 00:00:00'

        By default, the datetime instances returned are cftime.datetime
        objects, regardless of calendar.  If the only_use_cftime_datetimes
        keyword is set to False, they are datetime.datetime objects if the date
        falls in the Gregorian calendar (i.e. calendar is
        'proleptic_gregorian', 'standard' or gregorian' and the date is after
        1582-10-15). The datetime instances do not contain a time-zone offset,
        even if the specified unit contains one.

        Works for scalars, sequences and numpy arrays. Returns a scalar
        if input is a scalar, else returns a numpy array.

        Args:

        * time_value (float):
            Numeric time value/s. Maximum resolution is 1 second.

        Kwargs:

        * only_use_cftime_datetimes (bool):
            If True, will always return cftime datetime objects, regardless of
            calendar.  If False, returns datetime.datetime instances where
            possible.  Defaults to True.

        * only_use_python_datetimes (bool):
            If True, will always return datetime.datetime instances where
            possible, and raise an exception if not.  Ignored if
            only_use_cftime_datetimes is True.  Defaults to False.

        Returns:
            datetime, or numpy.ndarray of datetime object.

        For example:

            >>> import cf_units
            >>> u = cf_units.Unit('hours since 1970-01-01 00:00:00',
            ...                   calendar=cf_units.CALENDAR_STANDARD)
            >>> print(u.num2date(6))
            1970-01-01 06:00:00
            >>> dts = u.num2date([6, 7])
            >>> [str(dt) for dt in dts]
            ['1970-01-01 06:00:00', '1970-01-01 07:00:00']

        """

        return _num2date_to_nearest_second(
            time_value,
            self,
            only_use_cftime_datetimes=only_use_cftime_datetimes,
            only_use_python_datetimes=only_use_python_datetimes,
        )

    def num2pydate(self, time_value):
        """
        Convert time value(s) to python datetime.datetime objects, or raise an
        exception if this is not possible.  Same as::

            unit.num2date(time_value, only_use_cftime_datetimes=False,
                          only_use_python_datetimes=True)

        """
        return self.num2date(
            time_value,
            only_use_cftime_datetimes=False,
            only_use_python_datetimes=True,
        )
