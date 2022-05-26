# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Test function :func:`cf_units.num2date`."""


import pytest

from cf_units import num2date


class Test:
    def test_num2date_wrong_calendar(self):
        with pytest.raises(
            ValueError, match="illegal calendar or reference date"
        ):
            num2date(
                1,
                "days since 1970-01-01",
                calendar="360_day",
                only_use_cftime_datetimes=False,
                only_use_python_datetimes=True,
            )
