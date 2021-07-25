import sys
from distutils.sysconfig import get_config_var
from os import environ
from pathlib import Path
from shutil import copy

from setuptools import Command, Extension, setup

# Default to using cython, but use the .c files if it doesn't exist
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = False

COMPILER_DIRECTIVES = {}
DEFINE_MACROS = None
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
                message = f"clean: removing file {path}"
            else:
                message = f"clean: skipping file {path}"
            print(message)


def get_include_dirs():
    include_dirs = []
    include_dir = environ.get("UDUNITS2_INCDIR")
    if include_dir is None:
        include_dir = get_config_var("INCLUDEDIR")
    if include_dir is not None:
        include_dirs.append(include_dir)
    return include_dirs


def get_library_dirs():
    library_dirs = []
    library_dir = environ.get("UDUNITS2_LIBDIR")
    if library_dir is None:
        library_dir = get_config_var("LIBDIR")
    if library_dir is not None:
        library_dirs.append(library_dir)
    return library_dirs


def get_package_data():
    package_data = None
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
    DEFINE_MACROS = [("CYTHON_TRACE", "1"), ("CYTHON_TRACE_NOGIL", "1")]
    if FLAG_COVERAGE in sys.argv:
        sys.argv.remove(FLAG_COVERAGE)
    print('enable: "linetrace" Cython compiler directive')

library_dirs = get_library_dirs()

udunits_ext = Extension(
    f"{PACKAGE}._udunits2",
    [str(Path(f"{PACKAGE}") / f"_udunits2.{'pyx' if cythonize else 'c'}")],
    include_dirs=get_include_dirs(),
    library_dirs=library_dirs,
    libraries=["udunits2"],
    define_macros=DEFINE_MACROS,
    runtime_library_dirs=None
    if sys.platform.startswith("win")
    else library_dirs,
)

if cythonize:
    [udunits_ext] = cythonize(
        udunits_ext, compiler_directives=COMPILER_DIRECTIVES, language_level=2
    )

cmdclass = {"clean_cython": CleanCython, "build_ext": numpy_build_ext}

kwargs = dict(
    cmdclass=cmdclass,
    ext_modules=[udunits_ext],
    package_data=get_package_data(),
)

setup(**kwargs)
