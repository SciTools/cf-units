from __future__ import absolute_import, division, print_function

import os
import sys

from distutils.sysconfig import get_config_var
from setuptools import Command, Extension, find_packages, setup
import versioneer

# Default to using cython, but use the .c files if it doesn't exist
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = False

COMPILER_DIRECTIVES = {}
DEFINE_MACROS = None
FLAG_COVERAGE = '--cython-coverage'  # custom flag enabling Cython line tracing
BASEDIR = os.path.abspath(os.path.dirname(__file__))
NAME = 'cf-units'
CFUNITS_DIR = os.path.join(BASEDIR, 'cf_units')


class CleanCython(Command):
    description = 'Purge artifacts built by Cython'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for rpath, _, fnames in os.walk(CFUNITS_DIR):
            for fname in fnames:
                _, ext = os.path.splitext(fname)
                if ext in ('.pyc', '.pyo', '.c', '.so'):
                    artifact = os.path.join(rpath, fname)
                    if os.path.exists(artifact):
                        print('clean: removing file {!r}'.format(artifact))
                        os.remove(artifact)
                    else:
                        print('clean: skipping file {!r}'.format(artifact))


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


def load(fname):
    result = []
    with open(fname, 'r') as fi:
        result = [package.strip() for package in fi.readlines()]
    return result


def long_description():
    fname = os.path.join(BASEDIR, 'README.md')
    with open(fname, 'rb') as fi:
        result = fi.read().decode('utf-8')
    return result


include_dir = get_config_var('INCLUDEDIR')
include_dirs = [include_dir] if include_dir is not None else []
library_dir = get_config_var('LIBDIR')
library_dirs = [library_dir] if library_dir is not None else []

if sys.platform.startswith('win'):
    extra_extension_args = {}
else:
    extra_extension_args = dict(
        runtime_library_dirs=library_dirs)

ext = 'pyx' if cythonize else 'c'

if FLAG_COVERAGE in sys.argv or os.environ.get('CYTHON_COVERAGE', None):
    COMPILER_DIRECTIVES = {'linetrace': True}
    DEFINE_MACROS = [('CYTHON_TRACE', '1'),
                     ('CYTHON_TRACE_NOGIL', '1')]
    if FLAG_COVERAGE in sys.argv:
        sys.argv.remove(FLAG_COVERAGE)
    print('enable: "linetrace" Cython compiler directive')


def numpy_build_ext(pars):
    from setuptools.command.build_ext import build_ext as _build_ext

    class build_ext(_build_ext):
        def finalize_options(self):
            # See https://github.com/SciTools/cf-units/issues/151
            def _set_builtin(name, value):
                if isinstance(__builtins__, dict):
                    __builtins__[name] = value
                else:
                    setattr(__builtins__, name, value)

            _build_ext.finalize_options(self)
            _set_builtin('__NUMPY_SETUP__', False)
            import numpy
            self.include_dirs.append(numpy.get_include())

    return build_ext(pars)


udunits_ext = Extension('cf_units._udunits2',
                        ['cf_units/_udunits2.{}'.format(ext)],
                        include_dirs=include_dirs,
                        library_dirs=library_dirs,
                        libraries=['udunits2'],
                        define_macros=DEFINE_MACROS,
                        **extra_extension_args)

if cythonize:
    [udunits_ext] = cythonize(udunits_ext,
                              compiler_directives=COMPILER_DIRECTIVES,
                              language_level=2)

cmdclass = {'clean_cython': CleanCython, 'build_ext': numpy_build_ext}
cmdclass.update(versioneer.get_cmdclass())

description = ('Units of measure as required by the Climate and Forecast (CF) '
               'metadata conventions')

setup(
    name=NAME,
    version=versioneer.get_version(),
    url='https://github.com/SciTools/{}'.format(NAME),
    author='Met Office',
    description=description,
    long_description=long_description(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'cf_units': list(file_walk_relative('cf_units/etc',
                                                      remove='cf_units/'))},
    install_requires=load('requirements.txt'),
    setup_requires=['pytest-runner', 'numpy', 'cython'],
    tests_require=load('requirements-dev.txt'),
    test_suite='cf_units.tests',
    cmdclass=cmdclass,
    ext_modules=[udunits_ext]
    )
