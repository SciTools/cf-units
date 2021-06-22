# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
Miscellaneous utility functions.

"""

import abc
from collections.abc import Hashable


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
        if "_names" in namespace and not isinstance(
            namespace["_names"], abc.abstractproperty
        ):
            args = ", ".join(namespace["_names"])

            # Ensure the class has a constructor with explicit arguments.
            if "__init__" not in namespace:
                # Create a default __init__ method for the class
                method_source = (
                    "def __init__(self, %s):\n "
                    "self._init_from_tuple((%s,))" % (args, args)
                )
                exec(method_source, namespace)

            # Ensure the class has a "helper constructor" with explicit
            # arguments.
            if "_init" not in namespace:
                # Create a default _init method for the class
                method_source = (
                    "def _init(self, %s):\n "
                    "self._init_from_tuple((%s,))" % (args, args)
                )
                exec(method_source, namespace)

        return super(_MetaOrderedHashable, cls).__new__(
            cls, name, bases, namespace
        )


class _OrderedHashable(Hashable, metaclass=_MetaOrderedHashable):
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

    pass
