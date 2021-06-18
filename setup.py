from os import environ
from pathlib import Path
import sys

from distutils.sysconfig import get_config_var
from setuptools import Command, Extension, setup

# Default to using cython, but use the .c files if it doesn't exist
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = False

COMPILER_DIRECTIVES = {}
DEFINE_MACROS = None
FLAG_COVERAGE = '--cython-coverage'  # custom flag enabling Cython line tracing
BASEDIR = Path(__file__).parent.absolute()
CFUNITS_DIR = BASEDIR / 'cf_units'


class CleanCython(Command):
    description = 'Purge artifacts built by Cython'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for path in CFUNITS_DIR.rglob("*"):
            if path.suffix in ('.pyc', '.pyo', '.c', '.so'):
                message = f'clean: removing file {path}'
            else:
                message = f'clean: skipping file {path}'
            print(message)


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

if FLAG_COVERAGE in sys.argv or environ.get('CYTHON_COVERAGE', None):
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

kwargs = dict(
    cmdclass=cmdclass,
    ext_modules=[udunits_ext],
)

setup(**kwargs)
