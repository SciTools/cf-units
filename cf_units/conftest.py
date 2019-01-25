# (C) British Crown Copyright 2019, Met Office
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

"""
Configure pytest to ignore python 3 files in python 2.

"""
import os.path
import glob
import six


if six.PY2:
    here = os.path.dirname(__file__)
    all_parse_py = glob.glob(
        os.path.join(here, '_udunits2_parser', '*', '*.py'))
    all_compiled_parse_py = glob.glob(
        os.path.join(here, '_udunits2_parser', '*.py'))
    collect_ignore = list(all_parse_py) + list(all_compiled_parse_py)

    print(collect_ignore)
