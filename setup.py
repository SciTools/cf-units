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

rootpath = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return open(os.path.join(rootpath, *parts), 'r').read()


long_description = '{}'.format(read('README.rst'))

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
    long_description=long_description,
    classifiers=['Development Status :: 4 - Beta',
                 'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX',
                 'Operating System :: POSIX :: AIX',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Scientific/Engineering'],
    description='Units of measure as required by the Climate and Forecast (CF) metadata conventions',
)
