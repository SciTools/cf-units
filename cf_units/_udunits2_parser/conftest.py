"""
Configure pytest to ignore python 3 files in python 2.

"""
import os.path
import glob
import six


if six.PY2:
    here = os.path.dirname(__file__)
    all_py = glob.glob(os.path.join(here, '*.py'))
    parser_py = glob.glob(os.path.join(here, '*'))
    print(here)
    collect_ignore = list(all_py) + list(parser_py)
