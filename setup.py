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

setup(
    name='cf_units',
    version=extract_version(),
    url='https://github.com/SciTools/cf_units',
    author='UK Met Office',
    packages=['cf_units', 'cf_units/tests'],
    package_data={'cf_units': list(file_walk_relative('cf_units/etc',
                                                      remove='cf_units/'))},
    data_files=[('cf_units', ['COPYING', 'COPYING.LESSER'])],
    tests_require=['nose'],
)
