import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand
import versioneer


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
    return open(os.path.join(rootpath, *parts), 'r').read()


long_description = '{}'.format(read('README.rst'))

cmdclass = {'test': PyTest}
cmdclass.update(versioneer.get_cmdclass())

with open('requirements.txt') as f:
    require = f.readlines()
install_requires = [r.strip() for r in require]

setup(
    name='cf_units',
    version=versioneer.get_version(),
    url='https://github.com/SciTools/cf_units',
    author='UK Met Office',
    packages=['cf_units', 'cf_units/tests'],
    package_data={'cf_units': list(file_walk_relative('cf_units/etc',
                                                      remove='cf_units/'))},
    data_files=[('share/doc/cf_units',
                 ['COPYING', 'COPYING.LESSER', 'README.rst'])],
    install_requires=install_requires,
    tests_require=['pytest', 'pep8'],
    cmdclass=cmdclass
    )
