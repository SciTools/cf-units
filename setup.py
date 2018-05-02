from __future__ import absolute_import, division, print_function

import os
import sys

from setuptools import find_packages, setup
import versioneer


NAME = 'cf_units'
DIR = os.path.abspath(os.path.dirname(__file__))


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


def read(*parts):
    with open(os.path.join(DIR, *parts), 'rb') as f:
        return f.read().decode('utf-8')


require = read('requirements.txt')
install_requires = [r.strip() for r in require.splitlines()]


setup(
    name=NAME,
    version=versioneer.get_version(),
    url='https://github.com/SciTools/{}'.format(NAME),
    author='Met Office',
    description='Units of measure as required by the Climate and Forecast (CF) metadata conventions',
    long_description='{}'.format(read('README.rst')),
    packages=find_packages(),
    package_data={'cf_units': list(file_walk_relative('cf_units/etc',
                                                      remove='cf_units/'))},
    data_files=[('share/doc/cf_units',
                 ['COPYING', 'COPYING.LESSER', 'README.rst'])],
    install_requires=install_requires,
    tests_require=['pep8'],
    test_suite='{}.tests'.format(NAME),
    cmdclass=versioneer.get_cmdclass()
    )
