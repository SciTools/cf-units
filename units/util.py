# (C) British Crown Copyright 2010 - 2015, Met Office
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
Miscellaneous utility functions.

"""

from __future__ import (absolute_import, division, print_function)

import abc
import collections


def approx_equal(a, b, max_absolute_error=1e-10, max_relative_error=1e-10):
    """
    Returns whether two numbers are almost equal, allowing for the
    finite precision of floating point numbers.

    """
    # Deal with numbers close to zero
    if abs(a - b) < max_absolute_error:
        return True
    # Ensure we get consistent results if "a" and "b" are supplied in the
    # opposite order.
    max_ab = max([a, b], key=abs)
    relative_error = abs(a - b) / max_ab
    return relative_error < max_relative_error


class _MetaOrderedHashable(abc.ABCMeta):
    """
    A metaclass that ensures that non-abstract subclasses of _OrderedHashable
    without an explicit __init__ method are given a default __init__ method
    with the appropriate method signature.

    Also, an _init method is provided to allow subclasses with their own
    __init__ constructors to initialise their values via an explicit method
    signature.

    NB. This metaclass is used to construct the _OrderedHashable class as well
    as all its subclasses.

    """

    def __new__(cls, name, bases, namespace):
        # We only want to modify concrete classes that have defined the
        # "_names" property.
        if '_names' in namespace and \
                not isinstance(namespace['_names'], abc.abstractproperty):
            args = ', '.join(namespace['_names'])

            # Ensure the class has a constructor with explicit arguments.
            if '__init__' not in namespace:
                # Create a default __init__ method for the class
                method_source = ('def __init__(self, %s):\n '
                                 'self._init_from_tuple((%s,))' % (args, args))
                exec(method_source, namespace)

            # Ensure the class has a "helper constructor" with explicit
            # arguments.
            if '_init' not in namespace:
                # Create a default _init method for the class
                method_source = ('def _init(self, %s):\n '
                                 'self._init_from_tuple((%s,))' % (args, args))
                exec(method_source, namespace)

        return super(_MetaOrderedHashable, cls).__new__(
            cls, name, bases, namespace)


class _OrderedHashable(collections.Hashable):
    """
    Convenience class for creating "immutable", hashable, and ordered classes.

    Instance identity is defined by the specific list of attribute names
    declared in the abstract attribute "_names". Subclasses must declare the
    attribute "_names" as an iterable containing the names of all the
    attributes relevant to equality/hash-value/ordering.

    Initial values should be set by using ::
        self._init(self, value1, value2, ..)

    .. note::

        It's the responsibility of the subclass to ensure that the values of
        its attributes are themselves hashable.

    """

    # The metaclass adds default __init__ methods when appropriate.
    __metaclass__ = _MetaOrderedHashable

    @abc.abstractproperty
    def _names(self):
        """
        Override this attribute to declare the names of all the attributes
        relevant to the hash/comparison semantics.

        """
        pass

    def _init_from_tuple(self, values):
        for name, value in zip(self._names, values):
            object.__setattr__(self, name, value)

    def __repr__(self):
        class_name = type(self).__name__
        attributes = ', '.join('%s=%r' % (name, value)
                               for (name, value)
                               in zip(self._names, self._as_tuple()))
        return '%s(%s)' % (class_name, attributes)

    def _as_tuple(self):
        return tuple(getattr(self, name) for name in self._names)

    # Prevent attribute updates

    def __setattr__(self, name, value):
        raise AttributeError('Instances of %s are immutable' %
                             type(self).__name__)

    def __delattr__(self, name):
        raise AttributeError('Instances of %s are immutable' %
                             type(self).__name__)

    # Provide hash semantics

    def _identity(self):
        return self._as_tuple()

    def __hash__(self):
        return hash(self._identity())

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self._identity() == other._identity())

    def __ne__(self, other):
        # Since we've defined __eq__ we should also define __ne__.
        return not self == other

    # Provide default ordering semantics

    def __cmp__(self, other):
        if isinstance(other, _OrderedHashable):
            result = cmp(self._identity(), other._identity())
        else:
            result = NotImplemented
        return result
