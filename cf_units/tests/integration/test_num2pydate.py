# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""Test function :func:`cf_units.num2pydate`."""

import datetime
import unittest

from cf_units import num2pydate


class Test(unittest.TestCase):
    def test_num2pydate_simple(self):
        result = num2pydate(1, "days since 1970-01-01", calendar="standard")
        expected = datetime.datetime(1970, 1, 2)
        self.assertEqual(result, expected)
        self.assertIsInstance(result, datetime.datetime)

    def test_num2pydate_wrong_calendar(self):
        with self.assertRaisesRegex(
            ValueError, "illegal calendar or reference date"
        ):
            num2pydate(1, "days since 1970-01-01", calendar="360_day")


if __name__ == "__main__":
    unittest.main()
