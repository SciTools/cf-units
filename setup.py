import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def extract_version():
    version = None
    fdir = os.path.dirname(__file__)
    fnme = os.path.join(fdir, 'cf_units', '__init__.py')
    with open(fnme) as fd:
        for line in fd:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation characters.
                break
    return version


setup(
    name='cf_units',
    version=extract_version(),
    url='https://github.com/SciTools/cf_units',
    author='UK Met Office',
    packages=['cf_units', 'cf_units/tests'],
    data_files=[('cf_units', ['COPYING', 'COPYING.LESSER'])],
    tests_require=['nose'],
)
