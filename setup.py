"""Setup routines to enable cf-units' Cython elements.

All other setup configuration is in `pyproject.toml`.
"""

import sys
from distutils.sysconfig import get_config_var
from os import environ
from pathlib import Path
from shutil import copy

from setuptools import Command, Extension, setup

# Default to using cython, but use the .c files if it doesn't exist.
#  Supports the widest possible range of developer setups.
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = False

COMPILER_DIRECTIVES = {}
# This Cython macro disables a build warning, obsolete with Cython>=3
#  see : https://cython.readthedocs.io/en/latest/src/userguide/migrating_to_cy30.html#numpy-c-api
DEFINE_MACROS = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
FLAG_COVERAGE = "--cython-coverage"  # custom flag enabling Cython line tracing
BASEDIR = Path(__file__).resolve().parent
PACKAGE = "cf_units"
CFUNITS_DIR = BASEDIR / PACKAGE


class CleanCython(Command):
    description = "Purge artifacts built by Cython"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for path in CFUNITS_DIR.rglob("*"):
            if path.suffix in (".pyc", ".pyo", ".c", ".so"):
                msg = f"clean: removing file {path}"
                print(msg)
                path.unlink()


def get_dirs(env_var: str, config_var: str):
    """Get a directory from an env variable or a distutils config variable."""
    result = environ.get(env_var) or get_config_var(config_var)
    return [result] if result else []


def get_package_data():
    """Find and correctly package the UDUNITS2 XML files for a wheel build."""
    package_data = {}
    # Determine whether we're building a wheel.
    if "bdist_wheel" in sys.argv:
        # The protocol is that the UDUNITS2_XML_PATH environment variable
        # identifies the root UDUNITS2 XML file and parent directory containing
        # all the XML resource files that require to be bundled within this
        # wheel. Note that, this should match the UDUNITS2 distribution for the
        # UDUNITS2 library cf-units is linking against.
        xml_env = "UDUNITS2_XML_PATH"
        xml_database = environ.get(xml_env)
        if xml_database is None:
            emsg = f"Require to set {xml_env} for a cf-units wheel build."
            raise ValueError(emsg)
        xml_database = Path(xml_database)
        if not xml_database.is_file():
            emsg = (
                f"Can't open {xml_env} file {xml_database} "
                "during cf-units wheel build."
            )
            raise ValueError(emsg)
        # We have a valid XML file, so copy the distro bundle into the
        # cf_units/etc/share directory.
        xml_dir = xml_database.expanduser().resolve().parent
        share_base = Path("etc") / "share"
        share_dir = CFUNITS_DIR / share_base
        if not share_dir.is_dir():
            share_dir.mkdir(parents=True)
        else:
            # Purge any existing XML share files.
            [fname.unlink() for fname in share_dir.glob("*.xml")]
        # Bundle the UDUNITS2 XML file/s for the wheel.
        [copy(fname, share_dir) for fname in xml_dir.glob("*.xml")]
        # Register our additional wheel content.
        package_data = {PACKAGE: [str(share_base / "*.xml")]}
    return package_data


def numpy_build_ext(pars):
    """Make the NumPy headers available for the Cython layer."""
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
            _set_builtin("__NUMPY_SETUP__", False)
            import numpy

            self.include_dirs.append(numpy.get_include())

    return build_ext(pars)


if FLAG_COVERAGE in sys.argv or environ.get("CYTHON_COVERAGE", None):
    COMPILER_DIRECTIVES = {"linetrace": True}
    DEFINE_MACROS += [("CYTHON_TRACE", "1"), ("CYTHON_TRACE_NOGIL", "1")]
    if FLAG_COVERAGE in sys.argv:
        sys.argv.remove(FLAG_COVERAGE)
    print('enable: "linetrace" Cython compiler directive')

include_dirs = get_dirs("UDUNITS2_INCDIR", "INCLUDEDIR")
library_dirs = get_dirs("UDUNITS2_LIBDIR", "LIBDIR")

# Some of the complexity MUST remain in setup.py due to its dynamic nature. To
#  reduce confusion, the Extension is 100% defined here, rather than splitting
#  between setup.py and pyproject.toml `ext-modules`.
udunits_ext = Extension(
    f"{PACKAGE}._udunits2",
    [str(Path(f"{PACKAGE}") / f"_udunits2.{'pyx' if cythonize else 'c'}")],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=["udunits2"],
    define_macros=DEFINE_MACROS,
    runtime_library_dirs=(
        None if sys.platform.startswith("win") else library_dirs
    ),
)

if cythonize:
    # https://docs.cython.org/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
    [udunits_ext] = cythonize(
        udunits_ext,
        compiler_directives=COMPILER_DIRECTIVES,
        # Assert python 3 source syntax: Currently required to suppress a
        #  warning, even though this is now the default (as-of Cython v3).
        language_level="3str",
    )

cmdclass = {"clean_cython": CleanCython, "build_ext": numpy_build_ext}

kwargs = {
    "cmdclass": cmdclass,
    "ext_modules": [udunits_ext],
    "package_data": get_package_data(),
}

setup(**kwargs)
