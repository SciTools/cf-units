# [cf-units](https://cf-units.readthedocs.io/en/latest/)

#### Units of measure as defined by the Climate and Forecast (CF) Metadata Conventions.

|                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ⚙️ CI            | [![ci-locks](https://github.com/SciTools/cf-units/actions/workflows/ci-locks.yml/badge.svg?branch=main)](https://github.com/SciTools/cf-units/actions/workflows/ci-locks.yml)  [![ci-manifest](https://github.com/SciTools/cf-units/actions/workflows/ci-manifest.yml/badge.svg)](https://github.com/SciTools/cf-units/actions/workflows/ci-manifest.yml) [![ci-tests](https://github.com/SciTools/cf-units/actions/workflows/ci-tests.yml/badge.svg?branch=main)](https://github.com/SciTools/cf-units/actions/workflows/ci-tests.yml) [![ci-wheels](https://github.com/SciTools/cf-units/actions/workflows/ci-wheels.yml/badge.svg?branch=main)](https://github.com/SciTools/cf-units/actions/workflows/ci-wheels.yml) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/SciTools/cf-units/main.svg)](https://results.pre-commit.ci/latest/github/SciTools/cf-units/main) |
| 💬 Community     | [![GH Discussions](https://img.shields.io/badge/github-discussions%20%F0%9F%92%AC-yellow?logo=github&logoColor=lightgrey)](https://github.com/SciTools/cf-units/discussions)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 📖 Documentation | [![Documentation Status](https://readthedocs.org/projects/cf-units/badge/?version=latest)](https://cf-units.readthedocs.io/en/latest/?badge=latest)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 📈 Health        | [![Coverage Status](https://codecov.io/gh/SciTools/cf-units/branch/main/graph/badge.svg?token=6LlYlyTUZG)](https://codecov.io/gh/SciTools/cf-units)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ✨ Meta          | [![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/) [![Flake8](https://img.shields.io/badge/lint-flake8-lightgrey)](https://github.com/PyCQA/flake8) [![license - bds-3-clause](https://img.shields.io/github/license/SciTools/cf-units)](https://github.com/SciTools/cf-units/blob/main/LICENSE) [![Pixi Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json)](https://pixi.sh)                                                                                                                                                                                                                                            |
| 📦 Package       | [![conda-forge downloads](https://img.shields.io/conda/vn/conda-forge/cf-units?color=orange&label=conda-forge&logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/cf-units) [![pypi](https://img.shields.io/pypi/v/cf-units?color=orange&label=pypi&logo=python&logoColor=white)](https://pypi.org/project/cf-units/) [![pypi - python version](https://img.shields.io/pypi/pyversions/cf-units.svg?color=orange&logo=python&label=python&logoColor=white)](https://pypi.org/project/cf-units/) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1257902.svg)](https://doi.org/10.5281/zenodo.1257902)                                                                                                                                                                                                                                                                     |
| 🧰 Repo          | [![Commits since last release](https://img.shields.io/github/commits-since/SciTools/cf-units/latest.svg)](https://github.com/SciTools/cf-units/commits/main) [![contributors](https://img.shields.io/github/contributors/SciTools/cf-units)](https://github.com/SciTools/cf-units/graphs/contributors) [![Latest version](https://img.shields.io/github/tag/SciTools/cf-units)](https://github.com/SciTools/cf-units/releases)                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

## Table of Contents

[comment]: # (NOTE: toc auto-generated with
  https://github.com/jonschlinkert/markdown-toc
    $> markdown-toc -i --bullets='-' README.md)

[comment]: # (This entire README can be markdown linted with
  https://github.com/igorshubovych/markdownlint-cli
    $ markdownlint README.md)

- [Overview](#overview)
  - [Example](#example)
- [Get in Touch](#get-in-touch)
- [Credits, Copyright and License](#credits-copyright-and-license)

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

cf-units is released under a BSD-3 license. See [LICENSE](LICENSE) for full
terms.

The [Met Office](https://metoffice.gov.uk) has made a significant
contribution to the development, maintenance and support of this library.
All Met Office contributions are copyright on behalf of the British Crown.
