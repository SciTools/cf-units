# (C) British Crown Copyright 2021, Met Office
#
# This file is part of cf-units.
#
# cf-units is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cf-units is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cf-units.  If not, see <http://www.gnu.org/licenses/>.
"""Test function :func:`cf_units.date2num`."""

import unittest

from cf_units import num2date


class Test(unittest.TestCase):
    def test_num2date_wrong_calendar(self):
        with self.assertRaisesRegex(ValueError,
                                    'illegal calendar or reference date'):
            num2date(1, 'days since 1970-01-01', calendar='360_day',
                     only_use_cftime_datetimes=False,
                     only_use_python_datetimes=True)


if __name__ == '__main__':
    unittest.main()