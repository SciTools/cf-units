import os
import sys

import numpy as np
from setuptools import setup, Extension
from setuptools.command.test import test as TestCommand
import versioneer
from Cython.Distutils import build_ext
from distutils.sysconfig import get_config_var

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.verbose = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


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

rootpath = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(rootpath, *parts), 'rb') as f:
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

long_description = '{}'.format(read('README.rst'))

cmdclass = {'test': PyTest, 'build_ext': build_ext}
cmdclass.update(versioneer.get_cmdclass())
require = read('requirements.txt')
install_requires = [r.strip() for r in require.splitlines()]

setup(
    name='cf_units',
    version=versioneer.get_version(),
    url='https://github.com/SciTools/cf_units',
    author='Met Office',
    description='Units of measure as required by the Climate and Forecast (CF) metadata conventions',
    long_description=long_description,
    packages=['cf_units', 'cf_units/tests'],
    package_data={'cf_units': list(file_walk_relative('cf_units/etc',
                                                      remove='cf_units/'))},
    data_files=[('share/doc/cf_units',
                 ['COPYING', 'COPYING.LESSER', 'README.rst'])],
    install_requires=install_requires,
    tests_require=['pytest', 'pep8'],
    cmdclass=cmdclass,
    ext_modules=[udunits_ext]
    )
