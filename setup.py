import os
from distutils.core import setup


def extract_version():
    version = None
    fdir = os.path.dirname(__file__)
    fnme = os.path.join(fdir, 'units', '__init__.py')
    with open(fnme) as fd:
        for line in fd:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation characters.
                break
    return version


setup(
    name='units',
    version=extract_version(),
    url='http://scitools.org.uk/iris/',
    author='UK Met Office',
    packages=['units', 'units/tests'],
    data_files=[('units', ['COPYING', 'COPYING.LESSER'])],
    tests_require=['nose'],
)
