<h1 align='center'>
    cf-units
</h1>

<h4 align='center'>
    Units of measure as defined by the Climate and Forecast (CF) Metadata Conventions
</h4>

<p align='center'>
<a href='https://github.com/SciTools/cf-units/actions/workflows/ci-tests.yml'>
    <img src='https://github.com/SciTools/cf-units/actions/workflows/ci-tests.yml/badge.svg?branch=main'
         alt='ci-tests'>
</a>
<a href='https://github.com/SciTools/cf-units/actions/workflows/ci-wheels.yml'>
   <img src='https://github.com/SciTools/cf-units/actions/workflows/ci-wheels.yml/badge.svg?branch=main'
        alt='ci-wheels'>
</a>
<a href='https://github.com/SciTools/cf-units/actions/workflows/ci-locks.yml'>
   <img src='https://github.com/SciTools/cf-units/actions/workflows/ci-locks.yml/badge.svg?branch=main'
        alt='ci-locks>
</a>
<a href='https://cf-units.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/cf-units/badge/?version=latest'
         alt='Documentation Status' />
</a>
<a href='https://results.pre-commit.ci/latest/github/SciTools/cf-units/main'>
   <img src='https://results.pre-commit.ci/badge/github/SciTools/cf-units/main.svg'
        alt='pre-commit.ci'>
</a>
<a href='https://codecov.io/gh/SciTools/cf-units'>
   <img src='https://codecov.io/gh/SciTools/cf-units/branch/main/graph/badge.svg?token=6LlYlyTUZG'
        alt='codecov'>
</a>
</p>

<p align='center'>
<a href='https://anaconda.org/conda-forge/cf-units'>
   <img src='https://img.shields.io/conda/vn/conda-forge/cf-units?color=orange&label=conda-forge&logo=conda-forge&logoColor=white'
        alt='conda-forge'>
</a>
<a href='https://pypi.org/project/cf-units/'>
   <img src='https://img.shields.io/pypi/v/cf-units?color=orange&label=pypi&logo=python&logoColor=white'
        alt='pypi'>
</a>
<a href='https://github.com/SciTools/cf-units/releases'>
   <img src='https://img.shields.io/github/tag/SciTools/cf-units'
        alt='tags'>
</a>
<a href='https://github.com/SciTools/cf-units/commits/main'>
   <img src='https://img.shields.io/github/commits-since/SciTools/cf-units/latest.svg'
        alt='commits'>
</a>
<a href='https://github.com/SciTools/cf-units/graphs/contributors'>
   <img src='https://img.shields.io/github/contributors/SciTools/cf-units'
        alt='contributors'>
</a>
</p>

<p align='center'>
<a href='https://doi.org/10.5281/zenodo.3723086'>
   <img src='https://zenodo.org/badge/DOI/10.5281/zenodo.3723086.svg'
        alt='doi'>
</a>
<img src='https://img.shields.io/github/license/SciTools/cf-units'
     alt='licence'>
<a href='https://github.com/psf/black'>
   <img src='https://img.shields.io/badge/code%20style-black-000000'
        alt='black'>
</a>
<a href='https://github.com/PyCQA/flake8'>
    <img src='https://img.shields.io/badge/lint-flake8-lightgrey'
         alt='flake8'>
</a>
<a href='https://pycqa.github.io/isort/'>
   <img src='https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336'
        alt='isort'>
</a>
</p>

# Table of Contents

[comment]: # (NOTE: toc auto-generated with
  https://github.com/jonschlinkert/markdown-toc
    $> markdown-toc -i --bullets='-' README.md)

[comment]: # (This entire README can be markdown linted with
  https://github.com/igorshubovych/markdownlint-cli
    $ markdownlint README.md)

- [Overview](#overview)
  - [Example](#example)
- [Get in touch](#get-in-touch)
- [Credits, copyright and license](#credits-copyright-and-license)

## Overview

Units of measure as required by the Climate and Forecast (CF) metadata
conventions.

Provision of a wrapper class to support Unidata/UCAR UDUNITS-2 library, and the
cftime calendar functionality.

Documentation can be found at <https://cf-units.readthedocs.io/en/latest/>.

### Example

    >>> from cf_units import Unit
    >>> km = Unit('kilometers')
    >>> m = Unit('meters')
    >>> m.convert(1500, km)
    1.5

## Get in Touch

- Questions, ideas, general discussion or announcements
  of related projects: use the
  [Discussions space](https://github.com/SciTools/cf-units/discussions).
- Report bugs:
  [submit a GitHub issue](https://github.com/SciTools/cf-units/issues).
- Suggest features: see our [contributing guide](.github/CONTRIBUTING.md).

## Credits, Copyright and License

cf-units is developed collaboratively under the SciTools umbrella.

A full list of code contributors ("cf-units contributors") can be found at
https://github.com/SciTools/cf-units/graphs/contributors.

Code is just one of many ways of positively contributing to cf-units, please
see our [contributing guide](.github/CONTRIBUTING.md) for more details on how
you can get involved.

cf-units is released under a LGPL license with a shared copyright model.
See [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) for full terms.

The [Met Office](https://metoffice.gov.uk) has made a significant
contribution to the development, maintenance and support of this library.
All Met Office contributions are copyright on behalf of the British Crown.
