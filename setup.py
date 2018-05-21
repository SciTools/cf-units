from __future__ import absolute_import, division, print_function

import os
import sys

from Cython.Distutils import build_ext
from distutils.sysconfig import get_config_var
import numpy as np
from setuptools import setup, Extension, find_packages
import versioneer


NAME = 'cf_units'
DIR = os.path.abspath(os.path.dirname(__file__))


def file_walk_relative(top, remove=''):
    """
    Returns a generator of files from the top of the tree, removing
    the given prefix from the root/file result.

    """
    top = top.replace('/', os.path.sep)
    remove = remove.replace('/', os.path.sep)
    for root, dirs, files in os.walk(top):
        for file in files:
            yield os.path.join(root, file).replace(remove, '')


def read(*parts):
    with open(os.path.join(DIR, *parts), 'rb') as f:
        return f.read().decode('utf-8')

include_dir = get_config_var('INCLUDEDIR')
include_dirs = [include_dir] if include_dir is not None else []
library_dir = get_config_var('LIBDIR')
library_dirs = [library_dir] if library_dir is not None else []
if sys.platform.startswith('win'):
    extra_extension_args = {}
else:
    extra_extension_args = dict(
        runtime_library_dirs=library_dirs)
udunits_ext = Extension('cf_units._udunits2',
                        ['cf_units/_udunits2.pyx'],
                        include_dirs=include_dirs + [np.get_include()],
                        library_dirs=library_dirs,
                        libraries=['udunits2'],
                        **extra_extension_args)

cmdclass = {'build_ext': build_ext}
cmdclass.update(versioneer.get_cmdclass())

require = read('requirements.txt')
install_requires = [r.strip() for r in require.splitlines()]


setup(
    name=NAME,
    version=versioneer.get_version(),
    url='https://github.com/SciTools/{}'.format(NAME),
    author='Met Office',
    description='Units of measure as required by the Climate and Forecast (CF) metadata conventions',
    long_description='{}'.format(read('README.md')),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'cf_units': list(file_walk_relative('cf_units/etc',
                                                      remove='cf_units/'))},
    install_requires=install_requires,
    tests_require=['pep8'],
    test_suite='{}.tests'.format(NAME),
    cmdclass=cmdclass,
    ext_modules=[udunits_ext]
    )
